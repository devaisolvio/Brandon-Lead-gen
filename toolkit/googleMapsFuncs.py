"""
Google Maps Scraper using Apify
Uses compass/crawler-google-places actor
"""

import requests
import os
import time
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

essential_fields = [
        'title',
        'phone',
        'website',
        'address',
        'street',
        'city',
        'state',
        'postalCode',
        'countryCode',
        'totalScore',
        'reviewsCount',
        'categories',
        'categoryName',
        'url',

    ]
APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR_ID="compass~crawler-google-places"

def apify_google_maps_scraper(config, output_file_path, icp=None,location="us"):
    """
    Scrape Google Maps using Apify actor (compass/crawler-google-places)

    Args:
        config: Configuration dict for the Google Maps scraper
        output_file_path: Path to save the scraped data CSV
        icp: Ideal Customer Profile identifier (e.g., "Search for stadium")
    """
    print("🗺️ Starting Google Maps scraper (async)")
    
  
    
    try:
        # 1. Start actor asynchronously
        start_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs"
        
        print(f"🔗 Calling Apify API: {start_url}")
        
        start_resp = requests.post(
            start_url,
            params={"token": APIFY_TOKEN},
            json=config,
            headers={"Content-Type": "application/json"},
        )
        
        if not start_resp.ok:
            print(f"❌ Error response ({start_resp.status_code}): {start_resp.text}")
            start_resp.raise_for_status()
        
        run_id = start_resp.json()["data"]["id"]
        print(f"🆔 Run ID: {run_id}")
        
        # 2. Poll run status until completed
        print(f"⏳ Polling status for run {run_id}...")
        items = apify_actor_status(run_id)
        print(f"✅ Received {len(items)} items from Apify")
        
        # 3. Filter to only essential fields
        filtered_items = []
        for item in items:
            filtered_item = {field: item.get(field) for field in essential_fields}
            
            # Add ICP column if provided
            if icp:
                filtered_item['icp'] = icp
            if location:
                filtered_item['location']=location    
            
            filtered_items.append(filtered_item)
        
        # 4. Save results to CSV
        path = output_file_path
        output_dir = os.path.dirname(path)
        if output_dir:
            print(f"📂 Creating directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        
        df = pd.DataFrame(filtered_items)
        print(f"📊 DataFrame shape: {df.shape}")
        
        # Filter out permanently or temporarily closed businesses
        if 'permanentlyClosed' in df.columns:
            initial_count = len(df)
            df = df[df['permanentlyClosed'] != True]
            removed = initial_count - len(df)
            if removed > 0:
                print(f"🚫 Filtered out {removed} permanently closed businesses")
        
        if 'temporarilyClosed' in df.columns:
            initial_count = len(df)
            df = df[df['temporarilyClosed'] != True]
            removed = initial_count - len(df)
            if removed > 0:
                print(f"⏸️ Filtered out {removed} temporarily closed businesses")
        
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
        return df
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error:")
        print(f"   Status Code: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected Error:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        
        import traceback
        print(f"   Traceback:")
        traceback.print_exc()
        return None

def apify_actor_status(run_id):
    """
    Poll Apify actor status until completion and return results
    
    Args:
        run_id: The Apify run ID to check
        
    Returns:
        List of items from the completed run
    """
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    
    # Checking the status every 30 seconds until actor is completed
    while True:
        status_resp = requests.get(status_url, params={"token": APIFY_TOKEN})
        status_resp.raise_for_status()
        
        run_data = status_resp.json()["data"]
        status = run_data["status"]
        print(f"Status: {status}")
        
        if status == "SUCCEEDED":
            dataset_id = run_data["defaultDatasetId"]
            break
        
        if status in {"FAILED", "ABORTED", "TIMED-OUT"}:
            # Get error details
            error_info = run_data.get("statusMessage", "No error message available")
            print(f"Error details: {error_info}")
            raise RuntimeError(f"Google Maps scraper failed with status: {status}. Error: {error_info}")
        
        time.sleep(30)
    
    # 3. Fetch dataset items (REAL DATA)
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
    data_resp = requests.get(
        dataset_url,
        params={"token": APIFY_TOKEN, "format": "json"},
    )
    data_resp.raise_for_status()
    
    items = data_resp.json()
    return items


def scrape_google_maps_by_query(query, max_results=100, output_file_path="outputs/google_maps_results.csv", language="en", country_code="us", icp=None,location="us"):
    """
    Scrape Google Maps by search query

    Args:
        query: Search query string (e.g., "restaurants in New York")
        max_results: Maximum number of results to scrape
        output_file_path: Path to save results
        language: Language code (default: "en")
        country_code: Country code in lowercase (default: "us")
        icp: Ideal Customer Profile identifier (e.g., "Search for stadium")

    Returns:
        DataFrame with scraped results
    """
    config = {
        "searchStringsArray": [query],  # Actor expects searchStringsArray, not queries
        "maxCrawledPlacesPerSearch": max_results,
        "language": language,
        "countryCode": country_code.lower()  # Must be lowercase
    }
    

    return apify_google_maps_scraper(config, output_file_path, icp=icp,location=location)

