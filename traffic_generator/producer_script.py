import time
import pandas as pd
import requests
import json

CSV_FILE_PATH = "UNSW_NB15_ready_testing.csv"
INGESTION_API_URL = "http://localhost:8000/api/ingest"

def run_traffic_simulator():
    print(f"Reading dataset from {CSV_FILE_PATH}...")
    df = pd.read_csv(CSV_FILE_PATH)
    
    if 'attack_cat' in df.columns:
        df = df.drop(columns=['attack_cat', 'Label'], errors='ignore')

    print(f"Starting traffic stream to Ingestion Service... Total rows: {len(df)}")
    
    for index, row in df.iterrows():
        event_dict = row.to_dict()
        
        payload = [event_dict]
        
        try:
            response = requests.post(INGESTION_API_URL, json=payload)
            if response.status_code == 200:
                print(f"Sent row {index+1} successfully.")
            else:
                print(f"Failed row {index+1}: {response.text}")
        except Exception as e:
            print(f"Connection error: {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    run_traffic_simulator()