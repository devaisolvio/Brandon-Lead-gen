import requests

url = "https://api.instantly.ai/api/v2/emails"

query = {
  "limit": "100",
}

headers = {"Authorization": "Bearer Y2RmMjlmMDAtMWJhNy00ZDBiLTg4MGUtN2EzZTA4ZTQ3NzcxOlF2RE1wdlJTdVlPSA=="}

a = 0
while a < 1:
    response = requests.get(url, headers=headers, params=query)
    data = response.json()

    if len(data["items"]) < 100:
        break
    
    query["starting_after"] = data["items"][-1]["id"]
    
    for item in data["items"]:
        print(item["to_address_email_list"])
        print(item["subject"])

    a += 1


# data = response.json()
# print(data)
# print(len(data["items"]))

