from supabase import create_client, Client
import pandas as pd
import numpy as np
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

######## Create table from supabase ui using csv upload
######## Convert all the columns to text
######## Add a column called cooloff_period and set it to null

def check_if_lead_exists(email):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)

    response = supabase.table("LeadsTable").select("*").eq("email", email).execute()
    return response.data

def get_records_for_org(org_id):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)

    response = supabase.table("LeadsTable").select("*").eq("organization_id", org_id).execute()
    return response.data
# Takes in a single lead as a dictionary
# Checks if lead should be added with cooloff period or not
def insert_lead(lead):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)

    # Check if lead already exists - based on email address
    lead_exists = check_if_lead_exists(lead["email"])
    if lead_exists:
        print(f"Lead {lead['email']} already exists")
        return
    else:
        # Check if org already exists
        org_id = lead["organization_id"]
        records_for_org = get_records_for_org(org_id)

        # If org exists, copy the cooloff period
        if len(records_for_org) > 0:
            print(f"Org {org_id} already exists")
            print(records_for_org[0])
            lead["org_cooloff_period"] = records_for_org[0]["org_cooloff_period"]
            
        else:
            print(f"Org {org_id} does not exist")
            
        response = supabase.table("LeadsTable").insert(lead).execute()
    return response.data


# Need to insert one by one and check if lead should be added with cooloff period or not
def insert_leads_from_csv(file_path):
    df = pd.read_csv(file_path)
    # Converts every cell in the DataFrame to a string — no exceptions
    df = df.astype(str)

    # print(df.columns.tolist())
    dict_list = df.to_dict(orient="records")
    # print(dict_list[0])
    for row in dict_list:
        insert_lead(row)

def get_record_outside_cooloff_and_not_recently_retrieved(tableName, today_date, lead_cooloff_period):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)

    # Calculate the cooloff period for the lead
    lead_cooloff_period = datetime.datetime.now() + datetime.timedelta(days=lead_cooloff_period)
    lead_cooloff_date = lead_cooloff_period.strftime("%Y-%m-%d")

    response = (
        supabase
        .table(tableName)
        .select("*")
        .or_(f"org_cooloff_period.lt.{today_date},org_cooloff_period.is.null")
        .or_(f"lead_locked_till.lt.{lead_cooloff_date},lead_locked_till.is.null")
        .limit(1)
        .execute()
    )

    return response.data

def retrieve_single_lead(tableName, today_date, lead_cooloff_period, table_name):
    lead = get_record_outside_cooloff_and_not_recently_retrieved(tableName, today_date, lead_cooloff_period)
    if lead:
        print("Lead found", lead)
        update_cooloff_period_and_last_retrieved(lead[0]["unique_id"], today_date, lead_cooloff_period, lead[0]["organization_id"], table_name)
        return lead
    else:
        print("No lead found")

def retrieve_multiple_leads(tableName, today_date, lead_cooloff_period, table_name, num_leads):
    leads_retrieved = []
    for i in range(num_leads):
        lead = retrieve_single_lead(tableName, today_date, lead_cooloff_period, table_name)
        if lead:
            print("Lead found", lead)
            update_cooloff_period_and_last_retrieved(lead[0]["unique_id"], today_date, lead_cooloff_period, lead[0]["organization_id"], table_name)
            leads_retrieved.append(lead)
        else:
            print("No lead found")
    return leads_retrieved

def update_cooloff_period_and_last_retrieved(lead_id, today_date, lead_cooloff_period, organization_id, table_name):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)

    today_date = datetime.datetime.strptime(today_date, "%Y-%m-%d")
    lead_cooloff_date = today_date + datetime.timedelta(days=lead_cooloff_period)
    lead_cooloff_date_str = lead_cooloff_date.strftime("%Y-%m-%d")
    org_cooloff_date = today_date + datetime.timedelta(days=14)
    org_cooloff_date_str = org_cooloff_date.strftime("%Y-%m-%d")

    response = supabase.table(table_name).update({"org_cooloff_period": org_cooloff_date_str, "lead_locked_till": lead_cooloff_date_str}).eq("unique_id", lead_id).execute()

    # Update org cooloff period for all leads in the same org
    response = supabase.table(table_name).update({"org_cooloff_period": org_cooloff_date_str}).eq("organization_id", organization_id).execute()

    return response.data


# insert leads_df into supabase
# insert_leads_from_csv("outputs/cleaned.csv")

# retrieve leads that are not in cooloff period
# today = datetime.datetime.now().strftime("%Y-%m-%d")
# leads_retrieved = retrieve_multiple_leads("LeadsTable", today, 90, "LeadsTable", 10)
# leads_retrieved_df = pd.DataFrame(leads_retrieved)
# leads_retrieved_df.to_csv("outputs/leads_retrieved3.csv", index=False)