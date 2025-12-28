import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NEVERBOUNCE_API_KEY")

BASE_URL = "https://api.neverbounce.com/v4/jobs"


def start_job(emails):
    # Format according to NeverBounce docs - just array of email strings
    payload = {
        "key": API_KEY,
        "input_location": "supplied",
        "auto_start": 1,
        "auto_parse": 1,
        "input": [{"email": e} for e in emails],  # Changed format
    }

    print(f"Sending request to create job with {len(emails)} emails...")
    r = requests.post(f"{BASE_URL}/create", json=payload)
    
    # Print raw response for debugging
    print(f"Response status code: {r.status_code}")
    print(f"Response body: {r.text}")
    
    r.raise_for_status()
    response = r.json()
    
    # Check for errors in response
    if "status" in response and response["status"] != "success":
        error_msg = response.get("message", "Unknown error")
        raise Exception(f"NeverBounce API error: {error_msg}")
    
    if "job_id" not in response:
        raise Exception(f"NeverBounce API error: No job_id in response. Response: {response}")
    
    return response["job_id"]


def get_status(job_id):
    r = requests.get(
        f"{BASE_URL}/status",
        params={"key": API_KEY, "job_id": job_id},
    )
    
    # Print raw response for debugging
    print(f"Status check response: {r.text}")
    
    r.raise_for_status()
    response = r.json()
    
    # Check for errors in response
    if "status" in response and response["status"] != "success":
        error_msg = response.get("message", "Unknown error")
        raise Exception(f"NeverBounce API error: {error_msg}")
    
    # Return full job_status object for more details
    return response.get("job_status", "unknown"), response


def download_results(job_id, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    r = requests.get(
        f"{BASE_URL}/download",
        params={"key": API_KEY, "job_id": job_id},
    )
    
    print(f"Download response status: {r.status_code}")
    r.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(r.content)


def verify_emails(emails, output_path="outputs/verified.csv", max_wait_minutes=30):
    """
    Verify emails using NeverBounce API.
    
    Args:
        emails: List of email addresses to verify
        output_path: Path to save verification results
        max_wait_minutes: Maximum time to wait for job completion (default: 30 minutes)
    """
    print(f"Creating NeverBounce job for {len(emails)} emails...")
    job_id = start_job(emails)
    print(f"Job created with ID: {job_id}")
    
    max_iterations = (max_wait_minutes * 60) // 30  # Check every 30 seconds instead of 15
    iteration = 0
    
    while True:
        iteration += 1
        status, full_response = get_status(job_id)
        
        # Print detailed status info
        total = full_response.get("total", {})
        print(f"Job status (check {iteration}/{max_iterations}): {status}")
        if isinstance(total, dict):
            print(f"  Progress: {total.get('processed', 0)}/{total.get('records', 0)} records")
        
        if status == "complete":
            print("Job completed! Downloading results...")
            break
        elif status in ["failed", "error"]:
            raise Exception(f"NeverBounce job failed with status: {status}. Full response: {full_response}")
        elif status in ["uploading", "parsing", "running", "under_review", "waiting"]:
            # Job is still processing, continue waiting
            if iteration >= max_iterations:
                raise TimeoutError(
                    f"NeverBounce job timed out after {max_wait_minutes} minutes. "
                    f"Last status: {status}. Job ID: {job_id}"
                )
            time.sleep(30)  # Increased from 15 to 30 seconds
        else:
            # Unknown status - log warning but continue
            print(f"Warning: Unknown status '{status}', continuing to wait...")
            if iteration >= max_iterations:
                raise TimeoutError(
                    f"NeverBounce job timed out after {max_wait_minutes} minutes. "
                    f"Last status: {status}. Job ID: {job_id}"
                )
            time.sleep(30)
    
    download_results(job_id, output_path)
    print(f"Results downloaded to {output_path}")


def verify_apollo_final_emails(file_path):
    """
    Verify emails in apollo_final.csv using NeverBounce and add verification status column
    """
    print("Loading apollo_final.csv...")
    df = pd.read_csv(file_path)
    print(f"Total leads: {len(df)}")
    
    # Extract emails
    email_list = df["email"].dropna().astype(str).tolist()
    # Filter out empty strings and invalid emails
    email_list = [email.strip().lower() for email in email_list if email and email != 'nan' and '@' in email]
    
    # Remove duplicates to avoid redundant checks
    unique_emails = list(set(email_list))
    print(f"Total unique emails to verify: {len(unique_emails)} (from {len(email_list)} total)")
    
    if len(unique_emails) == 0:
        print("No emails to verify!")
        return df
    
    # Create temporary file for NeverBounce results
    temp_verified_path = "outputs/temp_neverbounce_results.csv"
    
    # Verify emails using NeverBounce
    print("Starting NeverBounce email verification...")
    print("This may take a few minutes...")
    verify_emails(unique_emails, temp_verified_path)
    
    # Read verification results
    print("Reading verification results...")
    try:
        # Try reading with header first
        verified_df = pd.read_csv(temp_verified_path)
        # If it doesn't have the expected columns, read without header
        if "email" not in verified_df.columns or len(verified_df.columns) < 2:
            verified_df = pd.read_csv(temp_verified_path, header=None)
            verified_df.columns = ["email", "status"]
    except Exception as e:
        print(f"Error reading verification results: {e}")
        # Fallback: read without header
        verified_df = pd.read_csv(temp_verified_path, header=None)
        verified_df.columns = ["email", "status"]
    
    verified_df["email"] = verified_df["email"].astype(str).str.strip().str.lower()
    
    # Create a mapping of email to status
    email_status_map = dict(zip(verified_df["email"], verified_df["status"]))
    
    # Add verification status column to original dataframe
    df["email_verification_status"] = df["email"].astype(str).str.strip().str.lower().map(email_status_map)
    
    # Fill NaN values (emails that weren't verified) with "unknown"
    df["email_verification_status"] = df["email_verification_status"].fillna("unknown")
    
    # Save back to the same file
    df.to_csv(file_path, index=False)
    
    # Print summary
    status_counts = df["email_verification_status"].value_counts()
    print(f"\nVerification complete! Status summary:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    # Clean up temporary file
    if os.path.exists(temp_verified_path):
        os.remove(temp_verified_path)
    
    print(f"\nUpdated {file_path} with email verification status")
    
    return df