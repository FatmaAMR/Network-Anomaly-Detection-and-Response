import streamlit as st
import pandas as pd
import httpx
import time
from datetime import datetime

st.set_page_config(page_title="NDR Dashboard", page_icon="🛡️", layout="wide")

DETECTION_API = "http://detection_service:8001/api/v1/alerts"

def fetch_alerts():
    try:
        response = httpx.get(DETECTION_API, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []

st.title("Network Detection & Response (NDR)")
st.markdown("Real-time network traffic analysis and anomaly detection.")

placeholder = st.empty()

while True:
    alerts = fetch_alerts()
    
    with placeholder.container():
        if not alerts:
            st.info("No active alerts detected. Monitoring network traffic...")
        else:
            df = pd.DataFrame(alerts)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
            
            col1, col2, col3 = st.columns(3)
            
            high_severity = len(df[df['severity'] == 'High'])
            
            col1.metric("Total Active Alerts", len(df))
            col2.metric("High Severity Alerts", high_severity, delta_color="inverse")
            col3.metric("Top Attack Category", df['attack_category'].mode()[0] if not df.empty else "N/A")
            
            st.markdown("### Recent Security Alerts")
            
            styled_df = df[['timestamp', 'srcip', 'dstip', 'attack_category', 'anomaly_score', 'severity']]
            st.dataframe(
                styled_df.style.applymap(
                    lambda x: 'background-color: #3b0000; color: #ffcccc' if x == 'High' else '', 
                    subset=['severity']
                ),
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("### Attack Distribution")
            attack_counts = df['attack_category'].value_counts()
            st.bar_chart(attack_counts, color="#FF6B00")
            
    time.sleep(3)