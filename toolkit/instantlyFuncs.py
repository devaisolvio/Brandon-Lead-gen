import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def export_instantly_leads(bool_starting_index_present, starting_index, selected_fields=None):
    apiKey = os.getenv("INSTANTLY_API_KEY")
    output_dir = os.getenv("OUTPUT_DIR", "outputs")
    url = "https://api.instantly.ai/api/v2/leads/list"

    payload = {"limit": 100}
    if bool_starting_index_present:
        payload["starting_after"] = starting_index

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apiKey}"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    df = pd.DataFrame(data["items"])
    
    # Auto-detect fields on first page
    if selected_fields is None:
        selected_fields = df.columns.tolist()
        print(f"Detected fields: {selected_fields}")
    
    # Only use fields that exist in this dataframe
    selected_fields = [f for f in selected_fields if f in df.columns]
    df = df[selected_fields]
    
    if bool_starting_index_present:
        df.to_csv(f"{output_dir}/instantly_leads.csv", mode="a", index=False, header=False)
    else:
        df.to_csv(f"{output_dir}/instantly_leads.csv", mode="w", index=False, header=True)

    return data.get("next_starting_after"), selected_fields

def export_paginated_instantly_leads(num_pages):
    next_starting_after = None
    selected_fields = None
    
    if num_pages == -1:
        num_pages = 10000
    
    count = 0
    while count < num_pages:
        print("Page: ", count)
        next_starting_after, selected_fields = export_instantly_leads(
            next_starting_after is not None, 
            next_starting_after,
            selected_fields
        )
        if next_starting_after is None:
            break
        count += 1

if __name__ == "__main__":
    export_paginated_instantly_leads(-1)