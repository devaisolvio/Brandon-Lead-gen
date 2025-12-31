from datetime import date
from toolkit.hubspotFuncs import get_contacts

from functions.file_upload import upload_csv_to_google_drive
INPUT_DIR = 'inputs'
OUTPUT_DIR = 'outputs'
PROMPTS_DIR = 'prompts'


#Output file path -Step 16 : Hubspot lead pull
output_hubspot_leads = f'{OUTPUT_DIR}/hubspot_leads.csv'

def run_hubspot_pipeline():
    """Run the complete HubSpot pipeline"""
    # Step 0: Get contacts from HubSpot
    get_contacts(output_hubspot_leads)
    
    # Step 1: Upload to Google Drive and delete local file
    upload_csv_to_google_drive(file_path=output_hubspot_leads, filename=f"Hubspot leads-{date.today().isoformat()}", delete_after_upload=True)
    
    print("\n" + "=" * 60)
    print("✅ HubSpot Pipeline Complete!")
    print("=" * 60)


# Run pipeline if executed directly
if __name__ == "__main__":
    skip = [0]
    
    if 0 not in skip:
        get_contacts(output_hubspot_leads)
    if 1 not in skip:
        upload_csv_to_google_drive(file_path=output_hubspot_leads, filename=f"Hubspot leads-{date.today().isoformat()}")                
        