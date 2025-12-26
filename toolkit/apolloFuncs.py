import json
import requests
import os
import time
import pandas as pd
from dotenv import load_dotenv
from datetime import date

# Load environment variables
load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR_ID = "code_crafter~leads-finder"

def apify_apollo_scraper(industry_key, config, output_apollo_scraped_file_path):
    print("🚀 Starting Apollo scraper (async)")
    print(f"📊 Industry: {industry_key}")
    print(f"📁 Output path: {output_apollo_scraped_file_path}")

    try:
        # 1️⃣ Start actor asynchronously
        start_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs"
        
        print(f"🔗 Calling Apify API: {start_url}")

        
        start_resp = requests.post(
            start_url,
            params={"token": APIFY_TOKEN},
            json=config,
            headers={"Content-Type": "application/json"},
        )
        
        
        start_resp.raise_for_status()

        run_id = start_resp.json()["data"]["id"]
        print(f"🆔 Run ID: {run_id}")

        # 2️⃣ Poll run status for the apify worker
        print(f"⏳ Polling status for run {run_id}...")
        items = apify_actor_status(run_id)

        # Add industry column to each field
        for item in items:
            item["industry"] = industry_key

        # Single master CSV
        path = output_apollo_scraped_file_path
        output_dir = os.path.dirname(path)
        
        if output_dir:  # Only create directory if path has a directory component
            print(f"📂 Creating directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)

        df = pd.DataFrame(items)
        print(f"📊 DataFrame shape: {df.shape}")

        # Append if file exists, else create
        file_exists = os.path.exists(path)
        print(f"📝 {'Appending to' if file_exists else 'Creating'} file: {path}")
        
        df.to_csv(
            path,
            mode="a",
            header=not file_exists,
            index=False
        )

        print(f"✅ Saved {len(df)} records to {path}")
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error for industry '{industry_key}':")
        print(f"   Status Code: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        print(f"   Config used: {json.dumps(config, indent=2)}")
        return False




def apify_actor_status(run_id):
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    
   #Checking the status in 30 sec to cehck if  actor is completed
   
    while True:
        status_resp = requests.get(status_url, params={"token": APIFY_TOKEN})
        status_resp.raise_for_status()

        run_data = status_resp.json()["data"]
        status = run_data["status"]
        print(f"⏳ Status: {status}")

        if status == "SUCCEEDED":
            dataset_id = run_data["defaultDatasetId"]
            break

        if status in {"FAILED", "ABORTED", "TIMED-OUT"}:
            raise RuntimeError(f"Apollo scraper failed with status: {status}")

        time.sleep(30)

    # 3️⃣ Fetch dataset items (REAL DATA)
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
    data_resp = requests.get(
        dataset_url,
        params={"token": APIFY_TOKEN, "format": "json"},
    )
    data_resp.raise_for_status()

    items = data_resp.json()
    return items
