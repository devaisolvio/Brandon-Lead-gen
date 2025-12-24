import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NEVERBOUNCE_API_KEY")

BASE_URL = "https://api.neverbounce.com/v4/jobs"


def start_job(emails):
    payload = {
        "key": API_KEY,
        "input_location": "supplied",
        "auto_start": 1,
        "auto_parse": 1,
        "input": [[e] for e in emails],
    }

    r = requests.post(f"{BASE_URL}/create", json=payload)
    r.raise_for_status()
    return r.json()["job_id"]


def get_status(job_id):
    r = requests.get(
        f"{BASE_URL}/status",
        params={"key": API_KEY, "job_id": job_id},
    )
    r.raise_for_status()
    return r.json()["job_status"]


def download_results(job_id, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    r = requests.get(
        f"{BASE_URL}/download",
        params={"key": API_KEY, "job_id": job_id},
    )
    r.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(r.content)


def verify_emails(emails, output_path="outputs/verified.csv"):
    job_id = start_job(emails)

    while get_status(job_id) != "complete":
        time.sleep(15)

    download_results(job_id, output_path)


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
    
    print(f"Total emails to verify: {len(email_list)}")
    
    if len(email_list) == 0:
        print("No emails to verify!")
        return df
    
    # Create temporary file for NeverBounce results
    temp_verified_path = "outputs/temp_neverbounce_results.csv"
    
    # Verify emails using NeverBounce
    print("Starting NeverBounce email verification...")
    print("This may take a few minutes...")
    verify_emails(email_list, temp_verified_path)
    
    # Read verification results
    print("Reading verification results...")
    try:
        # Try reading with header first
        verified_df = pd.read_csv(temp_verified_path)
        # If it doesn't have the expected columns, read without header
        if "email" not in verified_df.columns or len(verified_df.columns) < 2:
            verified_df = pd.read_csv(temp_verified_path, header=None)
            verified_df.columns = ["email", "status"]
    except:
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
