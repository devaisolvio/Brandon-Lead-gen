
from toolkit.cleaning import clean_data
from toolkit.instantlyFuncs import export_paginated_instantly_leads
from toolkit.scrapeAIFuncs import remove_non_ecommerce_companies
from toolkit.linkedInScraper import enrich_with_linkedin_data
from toolkit.apolloFuncs import apify_apollo_scraper

from functions.helper import recheck_duplicate_emails
from functions.built_with_helper import filter_builtwith_companies_by_instantly_companies
from functions.built_with_helper import import_leads_from_builtwith
from functions.helper import remove_unverified_emails
from functions.helper import check_against_previous_customers

from functions.apollo_input_data import industries



########################
# Input and Output dirs
########################
input_builtwith_leads_file_path = 'inputs/[Done]_All-Live-Hyros-Sites.csv'
apollo_filter_page = 'https://app.apollo.io/#/people?page=1&personTitles[]=founder&personTitles[]=cofounder&personTitles[]=ceo&excludedOrganizationKeywordFields[]=tags&excludedOrganizationKeywordFields[]=name&excludedOrganizationKeywordFields[]=social_media_description&sortAscending=false&sortByField=recommendations_score&qOrganizationSearchListId=68719818b04da50015b138bb'
output_import_list_file_path = 'outputs/importList.txt'
output_apollo_scraped_file_path = 'outputs/apollo_all_industries.csv/apollo_all_industries.csv'
output_cleaned_file_path = 'outputs/Secondary_Tier_1.csv'
output_verified_file_path = 'outputs/verified.csv'
output_verified_subsetted_file_path = 'outputs/verified_subsetted.csv'
output_instantly_leads_file_path = 'outputs/instantly_leads.csv'
output_builtwith_filtered_leads_file_path = 'outputs/builtwith_filtered_leads.csv'
output_rechecked_duplicates_file_path = 'outputs/rechecked_duplicates.csv'
output_scraped_ai_file_path = 'outputs/rechecked_duplicates.csv'
output_leads_bank_file_path = 'outputs/leads_bank.csv'
output_retrieved_leads_file_path = 'outputs/rechecked_duplicates.csv'
input_previous_customers_file_path = 'inputs/Previous_Customers_and_Samples_Given.csv'
output_rechecked_previous_customers_file_path = 'outputs/rechecked_previous_customers.csv'
output_company_tech_file_path = 'outputs/final_leads_with_tech.csv'
input_company_tech_file_path = 'inputs/grouped_by_domain.csv'
input_company_tech_file_path_2 = 'combined_output.csv'
output_linkedin_data_file_path = 'outputs/linkedin_enriched_leads.csv'
generate_personalizations_prompt_file_path = 'prompts/performance_marketers/generate_personalizations.txt'
select_one_prompt_file_path = 'prompts/performance_marketers/select_one.txt'

skip = [0,1,2,3,5,6,7,8,9,10,11,12]

if 0 not in skip:
    export_paginated_instantly_leads(-1)
#if 1 not in skip:
    filter_builtwith_companies_by_instantly_companies(input_builtwith_leads_file_path, output_instantly_leads_file_path, output_builtwith_filtered_leads_file_path)
#if 2 not in skip:
    import_leads_from_builtwith(output_builtwith_filtered_leads_file_path, output_import_list_file_path="outputs")
if 3 not in skip:
    for industry_obj in industries:
        for industry_key, config in industry_obj.items():
            print(f"Scraping {industry_key}...")
            apify_apollo_scraper(industry_key,config, output_apollo_scraped_file_path)

if 4 not in skip:
    clean_data(output_apollo_scraped_file_path, output_cleaned_file_path)

if 5 not in skip:
    recheck_duplicate_emails(output_cleaned_file_path, output_instantly_leads_file_path, output_rechecked_duplicates_file_path)
if 6 not in skip:
    remove_non_ecommerce_companies(output_rechecked_duplicates_file_path, output_scraped_ai_file_path)
if 7 not in skip:
    remove_unverified_emails(output_scraped_ai_file_path, output_verified_file_path, output_verified_subsetted_file_path)
if 10 not in skip:
    output_instantly_leads_file_path = 'outputs/instantly_leads.csv'
    check_against_previous_customers(output_retrieved_leads_file_path, input_previous_customers_file_path, output_instantly_leads_file_path, output_rechecked_previous_customers_file_path)

if 12 not in skip:
    enrich_with_linkedin_data(output_company_tech_file_path, output_linkedin_data_file_path, generate_personalizations_prompt_file_path, select_one_prompt_file_path)