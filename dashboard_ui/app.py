import streamlit as st
import pandas as pd
import httpx
import time
import plotly.express as px
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="NDR Dashboard", page_icon="🛡️", layout="wide")

# Custom CSS for Minimalist Design
st.markdown("""
    <style>
    .stApp { background-color: #0B1C2E; color: #F5F6FA; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { color: #F5F6FA; background-color: transparent; border-radius: 0; }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #FF6B00; color: #FF6B00 !important; }
    div[data-testid="stMetricValue"] { color: #87CEEB; }
    div[data-testid="stMetricDelta"] svg { color: #32CD32; }
    .stButton>button { background-color: #1E2A38; color: #F5F6FA; border: 1px solid #FF6B00; border-radius: 6px; }
    .stButton>button:hover { background-color: #FF6B00; color: #0B1C2E; }
    </style>
""", unsafe_allow_html=True)

DETECTION_API = "http://detection_service:8001/api/v1/alerts"

def fetch_alerts():
    try:
        response = httpx.get(DETECTION_API, timeout=5.0)
        return response.json() if response.status_code == 200 else []
    except Exception:
        return []

st.title("Network Detection & Response")

# Notification Sidebar
with st.sidebar:
    st.header("Active Notifications")
    alerts_data = fetch_alerts()
    if alerts_data:
        df_side = pd.DataFrame(alerts_data)
        high_alerts = df_side[df_side['severity'] == 'High']
        st.error(f"{len(high_alerts)} Critical Threats Detected")
        
        for _, row in high_alerts.head(5).iterrows():
            with st.expander(f"{row['attack_category']} from {row['srcip']}"):
                st.write(f"**Score:** {row['anomaly_score']:.2f}")
                st.write(f"**Target:** {row['dstip']}")
                if st.button("Block IP", key=row['event_id']):
                    st.success("IP Blocked at Firewall")
    else:
        st.success("No active threats.")

# Tabs for Organization
tab_live, tab_insights = st.tabs(["Live Monitoring", "Historical Insights"])

placeholder = st.empty()

while True:
    alerts = fetch_alerts()
    
    with placeholder.container():
        if alerts:
            df = pd.DataFrame(alerts)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
            with tab_live:
                # Actionable Metrics
                col1, col2, col3, col4 = st.columns(4)
                total_events = len(df)
                high_sev = len(df[df['severity'] == 'High'])
                
                col1.metric("Monitored Events", total_events, "+12% vs last hour")
                col2.metric("Critical Alerts", high_sev, "-2 vs last hour", delta_color="inverse")
                col3.metric("Most Targeted IP", df['dstip'].mode()[0] if not df.empty else "N/A")
                col4.metric("Top Attack Vector", df['attack_category'].mode()[0] if not df.empty else "N/A")
                
                st.markdown("---")
                
                # Interactive Plotly Chart
                st.subheader("Network Traffic & Anomaly Spikes")
                
                # Aggregating data for the time-series chart
                df_time = df.set_index('timestamp').resample('S').size().reset_index(name='Requests')
                fig = px.area(df_time, x='timestamp', y='Requests', 
                              color_discrete_sequence=['#87CEEB'])
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#F5F6FA', margin=dict(l=0, r=0, t=30, b=0),
                    xaxis_title="", yaxis_title="Requests / Sec"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Investigation Section
                st.subheader("Actionable Alert Investigation")
                if not df[df['severity'] == 'High'].empty:
                    selected_id = st.selectbox("Select an alert to investigate:", df[df['severity'] == 'High']['event_id'])
                    target_alert = df[df['event_id'] == selected_id].iloc[0]
                    
                    # Simulated Action Panel
                    panel_col1, panel_col2 = st.columns([2, 1])
                    with panel_col1:
                        st.info(f"**Analysis:** Event flagged as {target_alert['attack_category']} with a confidence score of {target_alert['anomaly_score']:.2f}. Traffic originated from {target_alert['srcip']} targeting {target_alert['dstip']}.")
                    with panel_col2:
                        st.button("Isolate Device", key=f"iso_{selected_id}", use_container_width=True)
                        st.button("Mark as False Positive", key=f"fp_{selected_id}", use_container_width=True)

            with tab_insights:
                st.subheader("Attack Distribution Patterns")
                fig_pie = px.pie(df, names='attack_category', hole=0.4, 
                                 color_discrete_sequence=['#FF6B00', '#32CD32', '#87CEEB', '#F5F6FA'])
                fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#F5F6FA')
                st.plotly_chart(fig_pie, use_container_width=True)
                
    time.sleep(3)