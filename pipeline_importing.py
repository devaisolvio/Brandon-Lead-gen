
from toolkit.cleaning import clean_data
from toolkit.instantlyFuncs import export_paginated_instantly_leads
from toolkit.scrapeAIFuncs import remove_non_ecommerce_companies
from toolkit.linkedInScraper import enrich_with_linkedin_data
from toolkit.apolloFuncs import apify_apollo_scraper
from toolkit.perplexityFuncs import evaluate_leads_with_perplexity,evaluate_gmaps_with_perplexity
from toolkit.neverBounceHTTP import verify_apollo_final_emails
from toolkit.googleMapsFuncs import scrape_google_maps_by_query
from toolkit.hubspotFuncs import get_contacts

from functions.helper import recheck_duplicate_emails
from functions.helper import filter_apollo_with_instantly_and_dedupe
from functions.built_with_helper import filter_builtwith_companies_by_instantly_companies
from functions.built_with_helper import import_leads_from_builtwith
from functions.helper import remove_unverified_emails
from functions.helper import check_against_previous_customers

from functions.apollo_input_data import industries
from functions.google_scraper_input_data import google_maps_scraping_icp


########################
# Input and Output Directories
########################
# Input files
INPUT_DIR = 'inputs'
OUTPUT_DIR = 'outputs'
PROMPTS_DIR = 'prompts'

# Input file paths
input_builtwith_leads_file_path = f'{INPUT_DIR}/builtwith_all_sites.csv'
input_previous_customers_file_path = f'{INPUT_DIR}/previous_customers.csv'
input_company_tech_file_path = f'{INPUT_DIR}/grouped_by_domain.csv'
input_company_tech_file_path_2 = f'{INPUT_DIR}/combined_output.csv'

# Apollo configuration
apollo_filter_page = 'https://app.apollo.io/#/people?page=1&personTitles[]=founder&personTitles[]=cofounder&personTitles[]=ceo&excludedOrganizationKeywordFields[]=tags&excludedOrganizationKeywordFields[]=name&excludedOrganizationKeywordFields[]=social_media_description&sortAscending=false&sortByField=recommendations_score&qOrganizationSearchListId=68719818b04da50015b138bb'

# Output file paths - Step 0-2: Instantly and BuiltWith
output_instantly_leads_file_path = f'{OUTPUT_DIR}/instantly_leads.csv'
output_builtwith_filtered_leads_file_path = f'{OUTPUT_DIR}/builtwith_filtered_leads.csv'
output_import_list_file_path = f'{OUTPUT_DIR}/apollo_import_list.txt'

# Output file paths - Step 3-4: Apollo scraping and filtering
output_apollo_scraped_file_path = f'{OUTPUT_DIR}/apollo_all_industries.csv'
output_apollo_final_file_path = f'{OUTPUT_DIR}/apollo_final.csv'

# Output file paths - Step 5: Data cleaning
output_cleaned_file_path = f'{OUTPUT_DIR}/apollo_cleaned.csv'

# Output file paths - Step 6-7: Duplicate checking and AI filtering
output_rechecked_duplicates_file_path = f'{OUTPUT_DIR}/apollo_deduplicated.csv'
output_scraped_ai_file_path = f'{OUTPUT_DIR}/apollo_ecommerce_filtered.csv'

# Output file paths - Step 8: Email verification
output_verified_file_path = f'{OUTPUT_DIR}/email_verification_results.csv'
output_verified_subsetted_file_path = f'{OUTPUT_DIR}/apollo_verified.csv'

# Output file paths - Step 9-10: Leads bank and previous customers
output_leads_bank_file_path = f'{OUTPUT_DIR}/leads_bank.csv'
output_retrieved_leads_file_path = f'{OUTPUT_DIR}/leads_retrieved.csv'
output_rechecked_previous_customers_file_path = f'{OUTPUT_DIR}/apollo_excluding_previous_customers.csv'

# Output file paths - Step 11-12: Tech stack and LinkedIn enrichment
output_company_tech_file_path = f'{OUTPUT_DIR}/apollo_with_tech_stack.csv'
output_linkedin_data_file_path = f'{OUTPUT_DIR}/apollo_linkedin_enriched.csv'

# Output file paths - Step 15: Google Maps scraping
output_google_maps_file_path = f'{OUTPUT_DIR}/google_maps_results.csv'

#Output file path -Step 16 : Hubspot lead pull
output_hubspot_leads = f'{OUTPUT_DIR}/hubspot_leads.csv'
# Prompt file paths
generate_personalizations_prompt_file_path = f'{PROMPTS_DIR}/performance_marketers/generate_personalizations.txt'
select_one_prompt_file_path = f'{PROMPTS_DIR}/performance_marketers/select_one.txt'

# Google Maps configuration
google_maps_query = "restaurants in New York"  # Update with your search query
google_maps_max_results = 2  # Maximum number of results to scrape

skip = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]  

if 0 not in skip:
    export_paginated_instantly_leads(-1)
if 3 not in skip:
    for industry_obj in industries:
        for industry_key, config in industry_obj.items():
            print(f"Scraping {industry_key}...")
            apify_apollo_scraper(industry_key,config, output_apollo_scraped_file_path)

# Step 4: Filter Apollo leads against Instantly leads and deduplicate
if 4 not in skip:
    filter_apollo_with_instantly_and_dedupe(output_apollo_scraped_file_path, output_instantly_leads_file_path, output_apollo_final_file_path)

# Step 5: Clean data
if 5 not in skip:
    clean_data(output_apollo_final_file_path, output_cleaned_file_path)

# Step 8: Remove unverified emails
if 8 not in skip:
    remove_unverified_emails(output_scraped_ai_file_path, output_verified_file_path, output_verified_subsetted_file_path)

# Step 10: Check against previous customers
if 10 not in skip:
    check_against_previous_customers(output_retrieved_leads_file_path, input_previous_customers_file_path, output_instantly_leads_file_path, output_rechecked_previous_customers_file_path)

# Step 13: Evaluate leads with Perplexity and score ICP match (0-10)
if 13 not in skip:
    evaluate_leads_with_perplexity(output_cleaned_file_path)

# Step 14: Verify emails in apollo_final.csv using NeverBounce
if 14 not in skip:
    verify_apollo_final_emails(output_cleaned_file_path)

# Step 15: Scrape Google Maps
if 15 not in skip:
    
    for query_obj in google_maps_scraping_icp:
        query =list(query_obj.keys())[0]
        locations = query_obj[query]['locations']
        
        for location in locations:
            print(f"Scraping Google Maps for: {query}-{location}")
            scrape_google_maps_by_query(
                query=f"{query} {location}",
                max_results=google_maps_max_results,
                output_file_path=output_google_maps_file_path,
                icp=query
            )       
   
#Step 16 : Qualify Google Maps leads with Perplexity
if 16 not in skip:
    evaluate_gmaps_with_perplexity(output_google_maps_file_path)

# Step 17 : Fetch the hubspot leads
if 17 not in skip:
    get_contacts(output_hubspot_leads)
            
        