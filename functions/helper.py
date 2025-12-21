import pandas as pd
from toolkit.neverBounceHTTP import verify_emails



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
    

