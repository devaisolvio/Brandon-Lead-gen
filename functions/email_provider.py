"""
Email Provider Functions
Individual functions for each email finding service
"""

import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
SNOV_API_USER_ID = os.getenv("SNOV_API_USER_ID", "")
SNOV_API_SECRET = os.getenv("SNOV_API_SECRET", "")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "")
ROCKETREACH_API_KEY = os.getenv("ROCKETREACH_API_KEY", "")


def hunter_find_email(domain):
    """Find email using Hunter.io"""
    if not domain or not HUNTER_API_KEY:
        return None
    
    try:
        response = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={"domain": domain, "api_key": HUNTER_API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and data['data'].get('emails'):
                emails = data['data']['emails']
                if emails:
                    for email_data in emails:
                        email = email_data.get('value')
                        if email and any(p in email.lower() for p in ['info@', 'contact@', 'hello@', 'support@']):
                            return email
                    return emails[0].get('value')
        return None
    except Exception:
        return None


def snov_find_email(domain):
    """Find email using Snov.io"""
    if not domain or not SNOV_API_USER_ID or not SNOV_API_SECRET:
        return None
    
    try:
        token_response = requests.post(
            "https://api.snov.io/v1/oauth/access_token",
            data={
                "grant_type": "client_credentials",
                "client_id": SNOV_API_USER_ID,
                "client_secret": SNOV_API_SECRET
            },
            timeout=10
        )
        
        if token_response.status_code != 200:
            return None
        
        token = token_response.json().get('access_token')
        if not token:
            return None
        
        response = requests.post(
            "https://api.snov.io/v1/get-domain-emails-with-info",
            json={"domain": domain, "type": "all", "limit": 10},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('emails') and len(data['emails']) > 0:
                emails = data['emails']
                for email_data in emails:
                    email = email_data.get('email')
                    if email and any(p in email.lower() for p in ['info@', 'contact@', 'hello@', 'support@']):
                        return email
                return emails[0].get('email')
        return None
    except Exception:
        return None


def apollo_find_email(domain):
    """Find email using Apollo.io"""
    if not domain or not APOLLO_API_KEY:
        return None
    
    try:
        response = requests.post(
            "https://api.apollo.io/v1/mixed_people/search",
            json={"organization_domains": [domain], "page": 1, "per_page": 1},
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": APOLLO_API_KEY
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('people') and len(data['people']) > 0:
                email = data['people'][0].get('email')
                if email:
                    return email
        return None
    except Exception:
        return None


def anymail_find_email(domain):
    """Find email using RocketReach"""
    if not domain or not ROCKETREACH_API_KEY:
        return None
    
    try:
        response = requests.get(
            "https://api.rocketreach.co/v2/api/search",
            params={"current_employer": domain, "page_size": 1},
            headers={"Api-Key": ROCKETREACH_API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('profiles') and len(data['profiles']) > 0:
                emails = data['profiles'][0].get('emails')
                if emails and len(emails) > 0:
                    return emails[0].get('email')
        return None
    except Exception:
        return None


def find_email_with_fallback(domain, delay=0.5):
    """
    Try multiple email finders until one succeeds
    Returns: (email, provider_name) or (None, None)
    """
    finders = [
        (hunter_find_email, "Hunter.io"),
        (snov_find_email, "Snov.io"),
        (apollo_find_email, "Apollo.io"),
        (anymail_find_email, "Anymail"),
    ]
    
    for finder_func, provider_name in finders:
        print(f"   Trying {provider_name}...")
        email = finder_func(domain)
        if email:
            return email, provider_name
        time.sleep(delay)
    
    return None, None
