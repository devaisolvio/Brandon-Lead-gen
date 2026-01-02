from datetime import date, datetime
from pathlib import Path
from typing import Dict
import os

from toolkit.hubspotFuncs import get_contacts
from toolkit.perplexityFuncs import evaluate_hubspot_with_perplexity
from toolkit.instantlyFuncs import export_paginated_instantly_leads
from functions.file_upload import upload_csv_to_google_drive
from functions.helper import filter_hubspot_with_instantly_and_dedupe,should_export_instantly_leads


BASE_DIR = Path(".")
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

FILES = {
    "hubspot_raw": OUTPUT_DIR / "hubspot_leads.csv",
    "hubspot_deduped": OUTPUT_DIR / "hubspot_leads_deduped.csv",
    "instantly": OUTPUT_DIR / "instantly_leads.csv",
}

def log(step: str, message: str):
    print(f"[{datetime.now().isoformat()}] {step} → {message}")



def run_hubspot_pipeline(skip_steps=None) -> Dict:
    """
    Run the complete HubSpot pipeline.
    Returns a summary dict for API / logging usage.
    """
    skip_steps = skip_steps or []

    result = {
        "pipeline": "hubspot",
        "started_at": datetime.now().isoformat(),
        "steps": {},
        "status": "running"
    }

    try:
        # Step 0: Export Instantly leads (if needed)
        if 0 not in skip_steps:
            if should_export_instantly_leads(FILES["instantly"]):
                log("STEP 0", "Exporting Instantly leads for deduplication")
                export_paginated_instantly_leads(-1)
                result["steps"]["export_instantly"] = "completed"
            else:
                log("STEP 0", "Skipping Instantly leads export (already run today)")
                result["steps"]["export_instantly"] = "skipped"

        # Step 1: Fetch contacts from HubSpot
        if 1 not in skip_steps:
            log("STEP 1", "Fetching contacts from HubSpot")
            get_contacts(str(FILES["hubspot_raw"]))
            result["steps"]["fetch_contacts"] = "completed"

        # Step 2: Deduplicate
        if 2 not in skip_steps:
            log("STEP 2", "Filtering & deduplicating leads")
            filter_hubspot_with_instantly_and_dedupe(
                input_hubspot_file_path=str(FILES["hubspot_raw"]),
                input_instantly_leads_file_path=str(FILES["instantly"]),
                output_hubspot_final_file_path=str(FILES["hubspot_deduped"]),
            )
            result["steps"]["dedupe"] = "completed"

        # Step 3: Evaluate with Perplexity
        if 3 not in skip_steps:
            log("STEP 3", "Evaluating leads with Perplexity")
            evaluate_hubspot_with_perplexity(str(FILES["hubspot_deduped"]))
            result["steps"]["perplexity"] = "completed"

        # Step 4: Upload
        if 4 not in skip_steps:
            log("STEP 4", "Uploading to Google Drive")
            upload_csv_to_google_drive(
                file_path=str(FILES["hubspot_deduped"]),
                filename=f"Hubspot leads - {date.today().isoformat()}",
                delete_after_upload=True
            )
            result["steps"]["upload"] = "completed"

        result["status"] = "completed"

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        log("ERROR", str(e))

    finally:
        result["completed_at"] = datetime.now().isoformat()

    return result



# Run pipeline if executed directly
if __name__ == "__main__":
    summary = run_hubspot_pipeline(skip_steps=[])
    print("\nPipeline Summary:")
    print(summary)
