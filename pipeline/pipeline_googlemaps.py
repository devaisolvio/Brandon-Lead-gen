from toolkit.googleMapsFuncs import scrape_google_maps_by_query
from toolkit.perplexityFuncs import evaluate_gmaps_with_perplexity
from toolkit.emailFinder import find_emails_for_leads

from functions.file_upload import upload_csv_to_google_drive
from functions.google_scraper_input_data import google_maps_scraping_icp
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

INPUT_DIR = 'inputs'
OUTPUT_DIR = 'outputs'
PROMPTS_DIR = 'prompts'

google_maps_max_results = 2  # Maximum number of results to scrape

# Output file paths - Step 15: Google Maps scraping
output_google_maps_file_path = f'{OUTPUT_DIR}/google_maps_results.csv'

def run_googlemaps_pipeline():
    """Run the complete Google Maps pipeline"""
    # Step 0: Google Maps Scraping
    for query_obj in google_maps_scraping_icp:
        query = list(query_obj.keys())[0]
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
    
    # Step 1: Qualify Google Maps leads with Perplexity
    evaluate_gmaps_with_perplexity(output_google_maps_file_path)
    
    # Step 2: Find Emails
    find_emails_for_leads(file_path=output_google_maps_file_path)
    
    # Step 3: Upload to Google Drive and delete local file
    print("\n" + "=" * 60)
    print("☁️  Step 3: Uploading to Google Drive")
    print("=" * 60)
    upload_csv_to_google_drive(file_path=output_google_maps_file_path, filename=f"google_maps_scraped_final-{date.today().isoformat()}", delete_after_upload=True)
    
    print("\n" + "=" * 60)
    print("✅ Google Maps Pipeline Complete!")
    print("=" * 60)


# Run pipeline if executed directly
if __name__ == "__main__":
    skip = [0, 1, 2, 3]
    
    if 0 not in skip:
        for query_obj in google_maps_scraping_icp:
            query = list(query_obj.keys())[0]
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
    if 1 not in skip:
        evaluate_gmaps_with_perplexity(output_google_maps_file_path)
    if 2 not in skip:
        find_emails_for_leads(file_path=output_google_maps_file_path)
    if 3 not in skip:
        upload_csv_to_google_drive(file_path=output_google_maps_file_path, filename=f"google_maps_scraped_final-{date.today().isoformat()}")
    
    print("\n" + "=" * 60)
    print("✅ Pipeline Complete!")
    print("=" * 60)