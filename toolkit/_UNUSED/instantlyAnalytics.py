import requests
import pandas as pd

def export_instantly_leads(bool_starting_index_present, starting_index, filter_type):
    apiKey = "Y2RmMjlmMDAtMWJhNy00ZDBiLTg4MGUtN2EzZTA4ZTQ3NzcxOlF2RE1wdlJTdVlPSA=="

    url = "https://api.instantly.ai/api/v2/leads/list"

    payload = {
        "limit": 100,
        "filter":filter_type
    }

    if bool_starting_index_present:
        payload["starting_after"] = starting_index

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {apiKey}"
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    print(data.keys())
    
    df = pd.DataFrame(data["items"])
    
    header_columns = df.columns.tolist()
    if bool_starting_index_present:
        df.to_csv(f"outputs/instantly_analytics_{filter_type}.csv", mode="a", index=False, header=False)
    else:
        df.to_csv(f"outputs/instantly_analytics_{filter_type}.csv", mode="w", index=False, header=header_columns)

    return data["next_starting_after"]

def get_campaign_details(id):
    url = "https://api.instantly.ai/api/v2/campaigns/" + id

    headers = {"Authorization": "Bearer Y2RmMjlmMDAtMWJhNy00ZDBiLTg4MGUtN2EzZTA4ZTQ3NzcxOlF2RE1wdlJTdVlPSA=="}

    response = requests.get(url, headers=headers)

    data = response.json()
    print(data)

def get_email_details(lead_email):
    url = "https://api.instantly.ai/api/v2/emails"

    query = {
    "limit": "15",
    "lead": lead_email,
    "email_type": "received"
    }

    headers = {"Authorization": "Bearer Y2RmMjlmMDAtMWJhNy00ZDBiLTg4MGUtN2EzZTA4ZTQ3NzcxOlF2RE1wdlJTdVlPSA=="}

    response = requests.get(url, headers=headers, params=query)

    data = response.json()
    return data


def export_paginated_instantly_leads(num_pages, filter_type):
    next_starting_after = None
    if num_pages == -1:
        num_pages = 10000
    count = 0
    while count < num_pages:
        print("c: ", count)
        next_starting_after = export_instantly_leads(next_starting_after is not None, next_starting_after, filter_type)
        print(next_starting_after)
        if next_starting_after is None:
            break
        
        count += 1

# filter_type = "FILTER_LEAD_NOT_INTERESTED"
# filter_type = "FILTER_LEAD_INTERESTED"
# export_paginated_instantly_leads(10000, filter_type)

# email_body_list = []
# df = pd.read_csv("outputs/instantly_analytics_FILTER_LEAD_INTERESTED.csv")
# for index, row in df.iterrows():
#     #get_campaign_details(row["campaign"])
#     a = get_email_details(row["email"])
#     #print(a["items"][0].keys())
#     body = a["items"][0]["body"]
#     email_body_list.append(body["text"])
#     print(index)

# df["email_body"] = email_body_list
# df.to_csv("outputs/instantly_analytics_FILTER_LEAD_INTERESTED_with_email_body.csv", index=False)
    
