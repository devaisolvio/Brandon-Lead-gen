from datetime import date, datetime
from pathlib import Path
from typing import Dict, List

from toolkit.googleMapsFuncs import scrape_google_maps_by_query
from toolkit.perplexityFuncs import evaluate_gmaps_with_perplexity
from toolkit.emailFinder import find_emails_for_leads

from functions.file_upload import upload_csv_to_google_drive
from functions.google_scraper_input_data import google_maps_scraping_icp

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(".")
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

FILES = {
    "google_maps": OUTPUT_DIR / "google_maps_results.csv",
}

GOOGLE_MAPS_MAX_RESULTS = 2
def log(step: str, message: str):
    print(f"[{datetime.now().isoformat()}] {step} → {message}")


def run_googlemaps_pipeline(skip_steps: List[int] = None) -> Dict:
    """
    Run the complete Google Maps pipeline.
    Returns structured result for Flask / monitoring.
    """
    skip_steps = skip_steps or []

    result = {
        "pipeline": "googlemaps",
        "started_at": datetime.now().isoformat(),
        "steps": {},
        "queries": {},
        "status": "running",
    }

    try:
        # STEP 0: Google Maps scraping (query + location safe)
        if 0 not in skip_steps:
            log("STEP 0", "Starting Google Maps scraping")

            for query_obj in google_maps_scraping_icp:
                query = list(query_obj.keys())[0]
                locations = query_obj[query]["locations"]

                result["queries"][query] = {}

                for location in locations:
                    try:
                        log("SCRAPE", f"{query} | {location}")
                        scrape_google_maps_by_query(
                            query=f"{query} {location}",
                            max_results=GOOGLE_MAPS_MAX_RESULTS,
                            output_file_path=str(FILES["google_maps"]),
                            icp=query,
                            location=location,
                        )
                        result["queries"][query][location] = "completed"
                    except Exception as e:
                        result["queries"][query][location] = f"failed: {str(e)}"
                        log("SCRAPE ERROR", f"{query} | {location} → {e}")

            result["steps"]["scraping"] = "completed"

        # STEP 1: AI qualification (Perplexity)
        if 1 not in skip_steps:
            log("STEP 1", "Evaluating leads with Perplexity")
            evaluate_gmaps_with_perplexity(str(FILES["google_maps"]))
            result["steps"]["perplexity"] = "completed"

        # STEP 2: Email finding
        if 2 not in skip_steps:
            log("STEP 2", "Finding emails for leads")
            find_emails_for_leads(file_path=str(FILES["google_maps"]))
            result["steps"]["email_finder"] = "completed"

        # STEP 3: Upload
        if 3 not in skip_steps:
            log("STEP 3", "Uploading results to Google Drive")
            upload_csv_to_google_drive(
                file_path=str(FILES["google_maps"]),
                filename=f"google_maps_scraped_final-{date.today().isoformat()}",
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
    summary = run_googlemaps_pipeline(skip_steps=[])
    print("\nPipeline Summary:")
    print(summary)
