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



def apify_apollo_scraper(industry_key,config, output_apollo_scraped_file_path):
    print("🚀 Starting Apollo scraper (async)")

    # 1️⃣ Start actor asynchronously
    start_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs"
    start_resp = requests.post(
        start_url,
        params={"token": APIFY_TOKEN},
        json=config,
        headers={"Content-Type": "application/json"},
    )
    start_resp.raise_for_status()

    run_id = start_resp.json()["data"]["id"]
    print(f"🆔 Run ID: {run_id}")

    # 2️⃣ Poll run status fo the apify worker
    items = apify_actor_status(run_id)

    # add industry column to each field
    for item in items:
        item["industry"] = industry_key

# single master CSV
    date_str = date.today().isoformat()
    path = os.path.join(output_apollo_scraped_file_path, f"apollo_all_industries.csv")

    os.makedirs(output_apollo_scraped_file_path, exist_ok=True)

    df = pd.DataFrame(items)

# append if file exists, else create
    df.to_csv(
    path,
    mode="a",
    header=not os.path.exists(path),
    index=False
)


    print(f"✅ Saved {len(df)} records to {output_apollo_scraped_file_path}")


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
