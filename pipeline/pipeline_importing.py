from datetime import date, datetime
from pathlib import Path
from typing import Dict, List

from toolkit.cleaning import clean_data
from toolkit.instantlyFuncs import export_paginated_instantly_leads
from toolkit.apolloFuncs import apify_apollo_scraper
from toolkit.perplexityFuncs import evaluate_leads_with_perplexity
from toolkit.neverBounceHTTP import verify_apollo_final_emails

from functions.helper import (
    filter_apollo_with_instantly_and_dedupe,
    remove_unverified_emails,
    check_against_previous_customers,
    should_export_instantly_leads
)
from functions.file_upload import upload_csv_to_google_drive
from functions.apollo_input_data import industries



BASE_DIR = Path(".")
INPUT_DIR = BASE_DIR / "inputs"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

FILES = {
    "previous_customers": INPUT_DIR / "previous_customers.csv",
    "instantly": OUTPUT_DIR / "instantly_leads.csv",
    "apollo_scraped": OUTPUT_DIR / "apollo_all_industries.csv",
    "apollo_deduped": OUTPUT_DIR / "apollo_deduped.csv",
    "apollo_clean": OUTPUT_DIR / "apollo_final.csv",
    "apollo_verified": OUTPUT_DIR / "apollo_verified.csv",
}

# Output file paths - Step 0-2: Instantly and BuiltWith
output_import_list_file_path = f'{OUTPUT_DIR}/apollo_import_list.txt'

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




def log(step: str, message: str):
    print(f"[{datetime.now().isoformat()}] {step} → {message}")

# Google Maps configuration

def run_apollo_pipeline(skip_steps: List[int] = None) -> Dict:
    """
    Run the complete Apollo pipeline.
    Returns structured result for Flask / monitoring.
    """
    skip_steps = skip_steps or []

    result = {
        "pipeline": "apollo",
        "started_at": datetime.now().isoformat(),
        "steps": {},
        "industries": {},
        "status": "running",
    }

    try:
        # STEP 0: Export Instantly leads
        if 0 not in skip_steps:
            if should_export_instantly_leads(FILES["instantly"]):
                log("STEP 0", "Exporting Instantly leads for deduplication")
                export_paginated_instantly_leads(-1)
                result["steps"]["export_instantly"] = "completed"
            else:
                log("STEP 0", "Skipping Instantly leads export (already run today)")
                result["steps"]["export_instantly"] = "skipped"

        # STEP 1: Apollo scraping (industry-safe)
        if 1 not in skip_steps:
            log("STEP 1", "Starting Apollo scraping")
            for industry_obj in industries:
                for industry_key, config in industry_obj.items():
                    try:
                        log("SCRAPE", f"{industry_key}")
                        apify_apollo_scraper(
                            industry_key,
                            config,
                            str(FILES["apollo_scraped"]),
                        )
                        result["industries"][industry_key] = "completed"
                    except Exception as e:
                        result["industries"][industry_key] = f"failed: {str(e)}"
                        log("SCRAPE ERROR", f"{industry_key} → {e}")

            result["steps"]["apollo_scraping"] = "completed"

        # STEP 2: Deduplication
        if 2 not in skip_steps:
            log("STEP 2", "Deduplicating Apollo leads")
            filter_apollo_with_instantly_and_dedupe(
                str(FILES["apollo_scraped"]),
                str(FILES["instantly"]),
                str(FILES["apollo_deduped"]),
            )
            result["steps"]["dedupe"] = "completed"

        # STEP 3: Cleaning
        if 3 not in skip_steps:
            log("STEP 3", "Cleaning data")
            clean_data(
                str(FILES["apollo_deduped"]),
                str(FILES["apollo_clean"]),
            )
            result["steps"]["cleaning"] = "completed"

        # STEP 4: Email verification
        if 4 not in skip_steps:
            log("STEP 4", "Verifying emails")
            verify_apollo_final_emails(str(FILES["apollo_clean"]))
            result["steps"]["email_verification"] = "completed"

        # STEP 5: Perplexity evaluation
        if 5 not in skip_steps:
            log("STEP 5", "Evaluating leads with Perplexity")
            evaluate_leads_with_perplexity(str(FILES["apollo_clean"]))
            result["steps"]["perplexity"] = "completed"

        # STEP 6: Upload
        if 6 not in skip_steps:
            log("STEP 6", "Uploading final file to Google Drive")
            upload_csv_to_google_drive(
                str(FILES["apollo_clean"]),
                filename=f"apollo_final-{date.today().isoformat()}",
                delete_after_upload=True,
            )
            result["steps"]["upload"] = "completed"

        result["status"] = "completed"

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        log("PIPELINE ERROR", str(e))

    finally:
        result["completed_at"] = datetime.now().isoformat()

    return result


# Run pipeline if executed directly
if __name__ == "__main__":
    summary = run_apollo_pipeline(skip_steps=[])
    print("\nPipeline Summary:")
    print(summary)

""" # Step 8: Remove unverified emails
if 8 not in skip:
    remove_unverified_emails(output_scraped_ai_file_path, output_verified_file_path, output_verified_subsetted_file_path)

# Step 10: Check against previous customers
if 10 not in skip:
    check_against_previous_customers(output_retrieved_leads_file_path, input_previous_customers_file_path, output_instantly_leads_file_path, output_rechecked_previous_customers_file_path)



 """