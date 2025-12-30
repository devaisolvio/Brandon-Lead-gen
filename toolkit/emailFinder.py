"""
Email Finder Main
Orchestrates email finding across multiple providers
"""

import pandas as pd
import time
import os
from urllib.parse import urlparse
from functions.email_provider import find_email_with_fallback


def extract_domain(website_url):
    """Extract domain from website URL"""
    if pd.isna(website_url) or not website_url:
        return None

    try:
        parsed = urlparse(website_url)
        domain = parsed.netloc or parsed.path
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return None


def find_emails_for_leads(
    file_path="outputs/google_maps_results.csv",
    delay_between_requests=1.0
):
    """
    Find emails for leads using multiple providers with fallback
    """
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    try:
        df = pd.read_csv(file_path)
        print(f"📊 Processing {len(df)} leads\n")

        if 'email' not in df.columns:
            df['email'] = None
        if 'email_source' not in df.columns:
            df['email_source'] = None

        emails_found = 0
        skipped = 0
        provider_stats = {}
        
        for index, row in df.iterrows():
            if pd.notna(row.get('email')) and row.get('email'):
                skipped += 1
                continue

            website = row.get('website')
            if pd.isna(website) or not website:
                continue

            domain = extract_domain(website)
            if not domain:
                continue

            title = row.get('title', 'Unknown')
            print(f"🔍 [{index + 1}/{len(df)}] {title} - {domain}")

            email, provider = find_email_with_fallback(domain)

            if email:
                df.at[index, 'email'] = email
                df.at[index, 'email_source'] = provider
                emails_found += 1
                provider_stats[provider] = provider_stats.get(provider, 0) + 1
                print(f"✅ Found: {email} (via {provider})\n")
            else:
                print(f"❌ No email found\n")

            if index < len(df) - 1:
                time.sleep(delay_between_requests)

        df.to_csv(file_path, index=False)
        
        print("=" * 50)
        print(f"✅ Complete! Found {emails_found} new emails")
        if skipped > 0:
            print(f"⏭️ Skipped {skipped} (already had emails)")
        
        if provider_stats:
            print("\n📊 Provider Statistics:")
            for provider, count in sorted(provider_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"   {provider}: {count} emails")
        
        print(f"💾 Updated {file_path}")
        print("=" * 50)

        return df

    except Exception as e:
        print(f"❌ Error: {e}")
        return None