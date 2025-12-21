import requests
import time
import os
from dotenv import load_dotenv
from toolkit.llmFuncs import llmCall

# Load environment variables from .env file
load_dotenv()

# Add these things: SERP API / Perplexity stuff

def queue_for_scraping(linkedin_url):
    # API endpoint
    url = "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_l1viktl72bvl7bjuj0&include_errors=true"

    # Headers
    headers = {
        "Authorization": f"Bearer {os.getenv('BRIGHTDATA_BEARER_TOKEN')}",
        "Content-Type": "application/json"
    }

    # JSON body
    payload = [
        {"url": linkedin_url}
    ]

    # POST request
    response = requests.post(url, headers=headers, json=payload)

    return response

def get_scraped_data(snapshot_id):
    # API endpoint
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"

    # Headers
    headers = {
        "Authorization": f"Bearer {os.getenv('BRIGHTDATA_BEARER_TOKEN')}",
    }

    # GET request
    response = requests.get(url, headers=headers)

    return response.json()

# expects a list of urls
# ["https://www.linkedin.com/in/dhruv-bais/", "https://www.linkedin.com/in/romain-torres-arcads/"...]
# returns a list of dictionaries with the url, data, and status
# [{'url': 'https://www.linkedin.com/in/dhruv-bais/', 'data': '...', 'status': 'done'}, {'url': 'https://www.linkedin.com/in/romain-torres-arcads/', 'data': '...', 'status': 'done'}]
def run_scraper_on_list_of_urls(urls):
    snapshot_ids = []
    output_data = []

    # Step 1: Queue all the URLs for scraping
    for url in urls:
        response = queue_for_scraping(url)
        payload = response.json()
        snapshot_id = payload['snapshot_id']
        snapshot_ids.append({
            'url': url,
            'snapshot_id': snapshot_id,
            'time_queued': time.time()
        })

    # Step 2: Poll repeatedly until all snapshots are processed
    timeout_minutes = 60
    poll_interval = 5  # seconds

    while len(snapshot_ids) > 0:
        i = 0
        while i < len(snapshot_ids):
            item = snapshot_ids[i]
            time_running = (time.time() - item['time_queued']) / 60

            if time_running > timeout_minutes:
                output_data.append({
                    'url': item['url'],
                    'data': '',
                    'status': 'timeout'
                })
                print(f"[TIMEOUT] {item['url']} after {time_running:.2f} mins")
                snapshot_ids.pop(i)
                continue  # don't increment i
            else:
                result = get_scraped_data(item['snapshot_id'])

                if isinstance(result, dict) and 'status' in result:
                    print(f"[PENDING] {item['url']} - status: {result['status']}")
                    i += 1  # not ready yet, keep it
                else:
                    output_data.append({
                        'url': item['url'],
                        'data': result,
                        'status': 'done'
                    })
                    print(f"[DONE] {item['url']}")
                    snapshot_ids.pop(i)
                    continue  # don't increment i

        time.sleep(poll_interval)  # wait before next round

    return output_data


#### Testing code ####
# linkedin_urls = ["http://www.linkedin.com/in/ivan-zhelev-a75a03182",
# "https://www.linkedin.com/in/dhruv-bais/",
# 'https://www.linkedin.com/in/romain-torres-arcads/'
# ]

# print(run_scraper_on_list_of_urls(linkedin_urls[2:]))


def enrich_with_linkedin_data(output_company_tech_file_path, output_linkedin_data_file_path, generate_personalizations_prompt_file_path, select_one_prompt_file_path):
    import pandas as pd

    df_company_tech = pd.read_csv(output_company_tech_file_path)
    df_company_tech = df_company_tech

    generate_personalizations_prompt = open(generate_personalizations_prompt_file_path, 'r').read()
    select_one_prompt = open(select_one_prompt_file_path, 'r').read()

    ######### Scrape the public linkedin profiles ###########
    linkedin_urls = []
    # get all the linkedin urls list
    for index, row in df_company_tech.iterrows():
        linkedin_url = row['linkedin_url']
        print(row)
        if linkedin_url is not None:
            linkedin_urls.append(linkedin_url)
        else:
            print("No linkedin url for", row['domain'])
    
    print(linkedin_urls)
    # run the scraper on the list of urls and get all the data
    linkedin_data = run_scraper_on_list_of_urls(linkedin_urls)

    ######### Generate the profile based personalization according to campaign 003_001 ###########
    personalizations = []
    # run the data through llm to generate profile based personalizations
    print("Generating personalizations for", len(linkedin_data), "leads")
    for linkedin_data_item in linkedin_data:
        generate_personalizations_prompt_with_data = generate_personalizations_prompt.replace('<<Profile>>', str(linkedin_data_item['data']))
        multiple_personalizations = llmCall(generate_personalizations_prompt_with_data)
        print(multiple_personalizations)
        select_one_prompt_with_data = select_one_prompt.replace('<<Profile>>', str(linkedin_data_item['data'])).replace('<<Generated Personalizations>>', multiple_personalizations)
        select_one_personalization = llmCall(select_one_prompt_with_data)
        print(select_one_personalization)
        personalizations.append({
            'linkedin_url': linkedin_data_item['url'],
            'personalization': select_one_personalization
        })

    # place the personalizations in the df_company_tech
    print(personalizations)
    df_company_tech['Linkedin Personalization'] = ''
    print("columns",df_company_tech.columns)
    df_linkedin_personalizations = pd.DataFrame(personalizations)
    print("df_linkedin_personalizations", df_linkedin_personalizations)
    for index, row in df_company_tech.iterrows():
        print(row)
        linkedin_url = row['linkedin_url']
        if linkedin_url in df_linkedin_personalizations['linkedin_url'].values:
            df_company_tech.at[index, 'Linkedin Personalization'] = df_linkedin_personalizations[df_linkedin_personalizations['linkedin_url'] == linkedin_url]['personalization'].values[0]
        else:
            print(linkedin_url, "not found in df_company_tech")

    ######### Select the industry proof personalization for each lead ###########
    # 

    df_company_tech.to_csv(output_linkedin_data_file_path, index=False)
    print(df_company_tech)
    print(df_linkedin_personalizations)
    

# input_builtwith_leads_file_path = 'inputs/All-Live-Shopify-Plus-Sites.csv'
# apollo_filter_page = 'https://app.apollo.io/#/people?page=1&personTitles[]=founder&personTitles[]=cofounder&personTitles[]=ceo&excludedOrganizationKeywordFields[]=tags&excludedOrganizationKeywordFields[]=name&excludedOrganizationKeywordFields[]=social_media_description&sortAscending=false&sortByField=recommendations_score&qOrganizationSearchListId=68719818b04da50015b138bb'
# output_import_list_file_path = 'outputs/importList.txt'
# output_apollo_scraped_file_path = 'outputs/apollo.csv'
# output_cleaned_file_path = 'outputs/cleaned.csv'
# output_verified_file_path = 'outputs/verified.csv'
# output_verified_subsetted_file_path = 'outputs/verified_subsetted.csv'
# output_instantly_leads_file_path = 'outputs/instantly_leads.csv'
# output_builtwith_filtered_leads_file_path = 'outputs/builtwith_filtered_leads.csv'
# output_rechecked_duplicates_file_path = 'outputs/rechecked_duplicates.csv'
# output_scraped_ai_file_path = 'outputs/scraped_ai_leads.csv'
# output_leads_bank_file_path = 'outputs/leads_bank.csv'
# output_retrieved_leads_file_path = 'outputs/retrieved_leads.csv'
# input_previous_customers_file_path = 'inputs/Previous_Customers_and_Samples_Given.csv'
# output_rechecked_previous_customers_file_path = 'outputs/rechecked_previous_customers.csv'
# output_company_tech_file_path = 'outputs/final_leads_with_tech.csv'
# input_company_tech_file_path = 'inputs/grouped_by_domain.csv'
# input_company_tech_file_path_2 = 'combined_output.csv'
# output_linkedin_data_file_path = 'outputs/linkedin_enriched_leads.csv'
# generate_personalizations_prompt_file_path = 'prompts/performance_marketers/generate_personalizations.txt'
# select_one_prompt_file_path = 'prompts/performance_marketers/select_one.txt'

# enrich_with_linkedin_data(output_company_tech_file_path, output_linkedin_data_file_path, generate_personalizations_prompt_file_path, select_one_prompt_file_path)