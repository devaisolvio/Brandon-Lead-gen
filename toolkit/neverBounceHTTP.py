import os
import time
import requests
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
