import requests
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

HUBSPOT_CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
HUBSPOT_TOKEN = os.getenv("HUBSPOT_API_KEY")


def get_contacts(output_hubspot_leads: str):
    headers = {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        HUBSPOT_CONTACTS_URL,
        headers=headers,
        timeout=30
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return {
            "status_code": response.status_code,
            "error": response.text
        }

    data = response.json()
    # data["results"] is a list of objects with a nested "properties" dict

    # 1) Normalize nested JSON to pull properties.*
    df_props = pd.json_normalize(data["results"])

    # 2) Keep only the fields we care about
    df = df_props[[
        "properties.firstname",
        "properties.lastname",
        "properties.email"
    ]].rename(columns={
        "properties.firstname": "firstname",
        "properties.lastname": "lastname",
        "properties.email": "email",
    })

    
    # 4) Keep only name + email if that's all you need
    """ df = df[["firstname","lastname", "email"]] """

    file_exists = os.path.exists(output_hubspot_leads)
    print(f"📝 {'Appending to' if file_exists else 'Creating'} file: {output_hubspot_leads}")

    df.to_csv(
        output_hubspot_leads,
        mode="a",
        header=not file_exists,
        index=False
    )

    print(f"✅ Saved {len(df)} records to {output_hubspot_leads}")
    return df
