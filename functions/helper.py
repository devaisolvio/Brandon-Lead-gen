import pandas as pd
import os
from toolkit.neverBounceHTTP import verify_emails
from datetime import datetime
from pathlib import Path


## Check the data from the apolo cleaned file and check with instantly and output a clean file of leads which are not contacted
def recheck_duplicate_emails(input_cleaned_file_path, input_instantly_leads_file_path, output_rechecked_duplicates_file_path):
    df_cleaned = pd.read_csv(input_cleaned_file_path)
    df_instantly = pd.read_csv(input_instantly_leads_file_path)
    print(df_cleaned.shape)
    print(df_cleaned.head())
    print(df_instantly.shape)
    print(df_instantly.head())

    # Ensure email columns are of string type and strip any whitespace
    df_cleaned['email'] = df_cleaned['email'].astype(str).str.strip().str.lower()
    df_instantly['email'] = df_instantly['email'].astype(str).str.strip().str.lower()

    # Filter df_cleaned to keep only emails not in df_instantly
    df_filtered = df_cleaned[~df_cleaned['email'].isin(df_instantly['email'])]

    print(df_filtered.shape)
    print(df_filtered.head())
    df_filtered.to_csv(output_rechecked_duplicates_file_path, index=False)

## Filter Apollo leads against Instantly leads and deduplicate Apollo data
def filter_apollo_with_instantly_and_dedupe(input_apollo_file_path, input_instantly_leads_file_path, output_apollo_final_file_path):
    """
    Filters out Apollo leads that exist in Instantly leads (by email, company_domain, or company_name)
    and deduplicates the remaining Apollo leads
    """
    print("Loading Apollo leads...")
    df_apollo = pd.read_csv(input_apollo_file_path)
    print(f"   Initial Apollo leads: {len(df_apollo)}")
    
    print("Loading Instantly leads...")
    df_instantly = pd.read_csv(input_instantly_leads_file_path)
    print(f"   Instantly leads: {len(df_instantly)}")
    
    # Normalize email columns for comparison
    df_apollo['email'] = df_apollo['email'].astype(str).str.strip().str.lower()
    df_instantly['email'] = df_instantly['email'].astype(str).str.strip().str.lower()
    
    # Normalize company_domain for comparison (handle NaN values)
    df_apollo['company_domain'] = df_apollo['company_domain'].astype(str).str.strip().str.lower()
    df_instantly['company_domain'] = df_instantly['company_domain'].astype(str).str.strip().str.lower()
    
    # Normalize company_name for comparison
    df_apollo['company_name'] = df_apollo['company_name'].astype(str).str.strip().str.lower()
    df_instantly['company_name'] = df_instantly['company_name'].astype(str).str.strip().str.lower()
    
    # Replace 'nan' strings with empty string for cleaner filtering
    df_apollo['company_domain'] = df_apollo['company_domain'].replace('nan', '')
    df_apollo['company_name'] = df_apollo['company_name'].replace('nan', '')
    df_instantly['company_domain'] = df_instantly['company_domain'].replace('nan', '')
    df_instantly['company_name'] = df_instantly['company_name'].replace('nan', '')
    
    # Create sets for faster lookup (exclude empty strings and 'nan')
    instantly_emails = set(df_instantly[df_instantly['email'].notna() & (df_instantly['email'] != '') & (df_instantly['email'] != 'nan')]['email'].unique())
    instantly_domains = set(df_instantly[df_instantly['company_domain'].notna() & (df_instantly['company_domain'] != '') & (df_instantly['company_domain'] != 'nan')]['company_domain'].unique())
    instantly_company_names = set(df_instantly[df_instantly['company_name'].notna() & (df_instantly['company_name'] != '') & (df_instantly['company_name'] != 'nan')]['company_name'].unique())
    
    # Filter out Apollo leads that match Instantly leads
    print("Filtering out leads already in Instantly...")
    # Start with all True, then filter out matches
    mask = pd.Series([True] * len(df_apollo), index=df_apollo.index)
    
    # Filter by email
    mask = mask & ~df_apollo['email'].isin(instantly_emails)
    # Filter by company_domain (only if domain is not empty)
    mask = mask & ~(df_apollo['company_domain'].isin(instantly_domains) & (df_apollo['company_domain'] != ''))
    # Filter by company_name (only if name is not empty)
    mask = mask & ~(df_apollo['company_name'].isin(instantly_company_names) & (df_apollo['company_name'] != ''))
    
    # Also filter out rows where email is 'nan' or empty
    mask = mask & (df_apollo['email'] != 'nan') & (df_apollo['email'] != '')
    
    df_filtered = df_apollo[mask].copy()
    print(f"   After filtering Instantly matches: {len(df_filtered)}")
    
    # Deduplicate Apollo leads by email (keep first occurrence)
    print("Deduplicating Apollo leads...")
    initial_count = len(df_filtered)
    df_filtered = df_filtered.drop_duplicates(subset=['email'], keep='first')
    duplicates_removed = initial_count - len(df_filtered)
    print(f"   Removed {duplicates_removed} duplicate emails")
    print(f"   Final Apollo leads: {len(df_filtered)}")
    
    # Save to output file
    df_filtered.to_csv(output_apollo_final_file_path, index=False)
    print(f"Saved filtered and deduplicated leads to {output_apollo_final_file_path}")

## Filter HubSpot leads against Instantly leads and deduplicate HubSpot data
def filter_hubspot_with_instantly_and_dedupe(input_hubspot_file_path, input_instantly_leads_file_path, output_hubspot_final_file_path):
    """
    Filters out HubSpot leads that exist in Instantly leads (by email)
    and deduplicates the remaining HubSpot leads
    """
    print("\n" + "=" * 60)
    print("🔄 Filtering HubSpot leads against Instantly leads")
    print("=" * 60)
    
    print("Loading HubSpot leads...")
    df_hubspot = pd.read_csv(input_hubspot_file_path)
    print(f"   Initial HubSpot leads: {len(df_hubspot)}")
    
    # Check if Instantly leads file exists
    if not os.path.exists(input_instantly_leads_file_path):
        print(f"⚠️  Warning: Instantly leads file not found at {input_instantly_leads_file_path}")
        print("   Skipping Instantly filtering. Will only deduplicate HubSpot leads.")
        df_instantly = pd.DataFrame(columns=['email'])
    else:
        print("Loading Instantly leads...")
        df_instantly = pd.read_csv(input_instantly_leads_file_path)
        print(f"   Instantly leads: {len(df_instantly)}")
    
    # Normalize email columns for comparison
    df_hubspot['email'] = df_hubspot['email'].astype(str).str.strip().str.lower()
    
    if len(df_instantly) > 0 and 'email' in df_instantly.columns:
        df_instantly['email'] = df_instantly['email'].astype(str).str.strip().str.lower()
        
        # Create set for faster lookup (exclude empty strings and 'nan')
        instantly_emails = set(df_instantly[
            df_instantly['email'].notna() & 
            (df_instantly['email'] != '') & 
            (df_instantly['email'] != 'nan')
        ]['email'].unique())
        
        # Filter out HubSpot leads that match Instantly leads
        print("Filtering out leads already in Instantly...")
        initial_count = len(df_hubspot)
        
        # Filter by email - exclude matches and invalid emails
        mask = (
            ~df_hubspot['email'].isin(instantly_emails) &
            (df_hubspot['email'] != 'nan') &
            (df_hubspot['email'] != '') &
            df_hubspot['email'].notna()
        )
        
        df_filtered = df_hubspot[mask].copy()
        filtered_count = initial_count - len(df_filtered)
        print(f"   Removed {filtered_count} leads that exist in Instantly")
        print(f"   After filtering Instantly matches: {len(df_filtered)}")
    else:
        print("   No Instantly leads to filter against. Skipping Instantly filtering.")
        # Still filter out invalid emails
        mask = (
            (df_hubspot['email'] != 'nan') &
            (df_hubspot['email'] != '') &
            df_hubspot['email'].notna()
        )
        df_filtered = df_hubspot[mask].copy()
        print(f"   Removed invalid emails. Remaining: {len(df_filtered)}")
    
    # Deduplicate HubSpot leads by email (keep first occurrence)
    print("Deduplicating HubSpot leads...")
    initial_count = len(df_filtered)
    df_filtered = df_filtered.drop_duplicates(subset=['email'], keep='first')
    duplicates_removed = initial_count - len(df_filtered)
    print(f"   Removed {duplicates_removed} duplicate emails")
    print(f"   Final HubSpot leads: {len(df_filtered)}")
    
    # Save to output file
    df_filtered.to_csv(output_hubspot_final_file_path, index=False)
    print(f"✅ Saved filtered and deduplicated leads to {output_hubspot_final_file_path}")
    print("=" * 60 + "\n")
    
# Check if the email is and verify it  and return only the verified emails    
def remove_unverified_emails(input_cleaned_file_path, output_verified_file_path, output_verified_subsetted_file_path):
    df = pd.read_csv(input_cleaned_file_path)
    email_list = df["email"].tolist()
    print(email_list)
    verify_emails(email_list, output_verified_file_path)
    verified_emails = pd.read_csv(output_verified_file_path, header=None)
    verified_emails.columns = ["email", "status"]
    print(verified_emails)
    verified_emails = verified_emails[verified_emails["status"] == "valid"]
    print(verified_emails)
    df = df[df["email"].isin(verified_emails["email"])]
    df.to_csv(output_verified_subsetted_file_path, index=False)
    
# Check if the lead is  previosuly contacted     
def check_against_previous_customers(input_retrieved_leads_file_path, input_previous_customers_file_path, output_instantly_leads_file_path, output_rechecked_previous_customers_file_path):
    df_retrieved_leads = pd.read_csv(input_retrieved_leads_file_path)
    df_previous_customers = pd.read_csv(input_previous_customers_file_path)
    
    print("df_retrieved_leads", df_retrieved_leads.shape)
    print("df_previous_customers", df_previous_customers.shape)
    print("df_retrieved_leads", df_retrieved_leads[["organization_website_url", "organization_name"]].head())
    print("df_previous_customers", df_previous_customers.head())

    drop_indices = []
    df_instantly_leads = pd.read_csv(output_instantly_leads_file_path)

    for index, row in df_retrieved_leads.iterrows():
        # clean the retrieved lead's company url
        company_url = str(row["organization_website_url"])
        company_url = company_url.lower()
        company_url = company_url.replace("https://", "")
        company_url = company_url.replace("http://", "")
        company_url = company_url.replace("www.", "")
        if(company_url[-1] == "/"):
            company_url = company_url[:-1]
        
        # check if the retrieved lead's company url is in the previous customers
        if(company_url in df_previous_customers["cleaned_company_url"].values):
            print("company_url", company_url)
            print("df_previous_customers", df_previous_customers[df_previous_customers["cleaned_company_url"] == company_url])
            drop_indices.append(index)
        # check if the retrieved lead's company name is in the previous customers
        if(row["organization_name"] in df_previous_customers["Company Name"].values):
            drop_indices.append(index)

        # check if the email is in instantly prior emails
        if(row["email"] in df_instantly_leads["email"].values):
            drop_indices.append(index)

    df_retrieved_leads = df_retrieved_leads.drop(drop_indices)
    df_retrieved_leads.to_csv(output_rechecked_previous_customers_file_path, index=False)

# Clean data of the previous companies
def clean_previous_customers(input_previous_customers_file_path):
        
    df_previous_customers = pd.read_csv(input_previous_customers_file_path)
    cleaned_company_urls = []
    for index, row in df_previous_customers.iterrows():
        company_url = row["Website URL"]
        company_url = company_url.lower()
        company_url = company_url.replace("https://", "")
        company_url = company_url.replace("http://", "")
        company_url = company_url.replace("www.", "")
        if(company_url[-1] == "/"):
            company_url = company_url[:-1]
        cleaned_company_urls.append(company_url)

    df_previous_customers["cleaned_company_url"] = cleaned_company_urls
    df_previous_customers.to_csv(input_previous_customers_file_path, index=False)    
    


def should_export_instantly_leads(instantly_file: Path) -> bool:
    """
    Check if Instantly leads should be exported.
    Returns True if file doesn't exist or wasn't created today.
    """
    if not instantly_file.exists():
        return True
    
    # Get file modification time
    file_mtime = datetime.fromtimestamp(os.path.getmtime(instantly_file))
    today = datetime.now().date()
    file_date = file_mtime.date()
    
    if file_date < today:
        return True
    else:
        return False