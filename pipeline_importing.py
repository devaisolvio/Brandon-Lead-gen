
from toolkit.cleaning import clean_data
from toolkit.instantlyFuncs import export_paginated_instantly_leads
from toolkit.apolloFuncs import apify_apollo_scraper
from toolkit.perplexityFuncs import evaluate_leads_with_perplexity
from toolkit.neverBounceHTTP import verify_apollo_final_emails


from functions.helper import filter_apollo_with_instantly_and_dedupe
from functions.helper import remove_unverified_emails
from functions.helper import check_against_previous_customers

from functions.apollo_input_data import industries



########################
# Input and Output Directories
########################
# Input files
INPUT_DIR = 'inputs'
OUTPUT_DIR = 'outputs'
PROMPTS_DIR = 'prompts'

# Input file paths
input_previous_customers_file_path = f'{INPUT_DIR}/previous_customers.csv'


# Output file paths - Step 0-2: Instantly and BuiltWith
output_instantly_leads_file_path = f'{OUTPUT_DIR}/instantly_leads.csv'
output_import_list_file_path = f'{OUTPUT_DIR}/apollo_import_list.txt'

# Output file paths - Step 3-4: Apollo scraping and filtering
output_apollo_scraped_file_path = f'{OUTPUT_DIR}/apollo_all_industries.csv'
output_apollo_deduped_file_path = f'{OUTPUT_DIR}/apollo_deduped.csv'

# Output file paths - Step 5: Data cleaning
output_final_file_path = f'{OUTPUT_DIR}/apollo_final.csv'

# Output file paths - Step 6-7: Duplicate checking and AI filtering
output_rechecked_duplicates_file_path = f'{OUTPUT_DIR}/apollo_deduplicated.csv'
output_scraped_ai_file_path = f'{OUTPUT_DIR}/apollo_ecommerce_filtered.csv'

# Output file paths - Step 8: Email verification
output_verified_file_path = f'{OUTPUT_DIR}/email_verification_results.csv'
output_verified_subsetted_file_path = f'{OUTPUT_DIR}/apollo_verified.csv'

# Output file paths - S previous customers
output_rechecked_previous_customers_file_path = f'{OUTPUT_DIR}/apollo_excluding_previous_customers.csv'





# Google Maps configuration


skip = [0,1,2,3,4,5,8,10,]  

if 0 not in skip:
    export_paginated_instantly_leads(-1)
if 1 not in skip:
    for industry_obj in industries:
        for industry_key, config in industry_obj.items():
            print(f"Scraping {industry_key}...")
            apify_apollo_scraper(industry_key,config, output_apollo_scraped_file_path)

# Step 4: Filter Apollo leads against Instantly leads and deduplicate
if 2 not in skip:
    filter_apollo_with_instantly_and_dedupe(output_apollo_scraped_file_path, output_instantly_leads_file_path, output_apollo_deduped_file_path)

# Step 5: Clean data
if 3 not in skip:
    clean_data(output_apollo_deduped_file_path, output_final_file_path)
    
if 4 not in skip:
    verify_apollo_final_emails(output_final_file_path)

if 5 not in skip:
    evaluate_leads_with_perplexity(output_final_file_path)
    

""" # Step 8: Remove unverified emails
if 8 not in skip:
    remove_unverified_emails(output_scraped_ai_file_path, output_verified_file_path, output_verified_subsetted_file_path)

# Step 10: Check against previous customers
if 10 not in skip:
    check_against_previous_customers(output_retrieved_leads_file_path, input_previous_customers_file_path, output_instantly_leads_file_path, output_rechecked_previous_customers_file_path)



 """