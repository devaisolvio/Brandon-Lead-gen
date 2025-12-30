from toolkit.googleMapsFuncs import scrape_google_maps_by_query
from toolkit.perplexityFuncs import evaluate_gmaps_with_perplexity
from toolkit.emailFinder import find_emails_for_leads
from functions.google_scraper_input_data import google_maps_scraping_icp


INPUT_DIR = 'inputs'
OUTPUT_DIR = 'outputs'
PROMPTS_DIR = 'prompts'


google_maps_max_results = 2  # Maximum number of results to scrape

# Output file paths - Step 15: Google Maps scraping
output_google_maps_file_path = f'{OUTPUT_DIR}/google_maps_results.csv'

skip=[0,1]


if 0 not in skip:
    
    for query_obj in google_maps_scraping_icp:
        query =list(query_obj.keys())[0]
        locations = query_obj[query]['locations']
        
        for location in locations:
            print(f"Scraping Google Maps for: {query}-{location}")
            scrape_google_maps_by_query(
                query=f"{query} {location}",
                max_results=google_maps_max_results,
                output_file_path=output_google_maps_file_path,
                icp=query,
                location=location
            )       
   
#Step 16 : Qualify Google Maps leads with Perplexity
if 1 not in skip:
    evaluate_gmaps_with_perplexity(output_google_maps_file_path)

if 2 not in skip:
     find_emails_for_leads(
        file_path="outputs/google_maps_results.csv",
      
    )  