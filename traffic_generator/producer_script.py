import pandas as pd
import requests
import time
import os

CSV_PATH = "./Cleaned_UNSW-NB15.csv"
INGESTION_URL = "http://localhost:8000/api/ingest"

def stream_real_traffic():
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    print(f"Loading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH, nrows=1000) 
    
    print(f"Loaded {len(df)} rows. Starting simulation...")
    
    for index, row in df.iterrows():
        event = row.to_dict()
        
        event["timestamp"] = time.time()
        if "srcip" not in event: 
            event["srcip"] = "192.168.1.50"
        if "dstip" not in event: 
            event["dstip"] = "10.0.0.5"

        try:
            response = requests.post(INGESTION_URL, json=[event])
            if response.status_code == 200:
                print(f"[{index}] Sent event successfully.")
            else:
                print(f"Failed to send row {index}: {response.text}")
        except Exception as e:
            print(f"Connection error: {e}")
            
        time.sleep(1)

if __name__ == "__main__":
    stream_real_traffic()