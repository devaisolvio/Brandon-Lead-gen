import pandas as pd
from toolkit.llmFuncs import llmCall
import time

def normalize_apollo_columns(df):
    df = df.copy()

    df["title"] = df["job_title"]
    df["organization_name"] = df["company_name"]
    df["organization_website_url"] = df["company_website"]
    df["organization_short_description"] = df["company_description"]

    return df




def clean_data(input_apollo_scraped_file_path, output_cleaned_file_path):
    df = pd.read_csv(input_apollo_scraped_file_path)
    df = normalize_apollo_columns(df)
    df = clean_website_links(df) 
    df = clean_titles(df)
    df = clean_emails(df)
    df = clean_company_names(df)

    df.to_csv(output_cleaned_file_path, index=False)

def clean_titles(df):
    # Cleaning the title column
    newTitle = []
    dropIndices = []
    for index, row in df.iterrows():
        if(pd.isna(row["title"])):
            newTitle.append("N/A")
            dropIndices.append(index)
            continue
        
        if("owner" in row["title"].lower()):
            newTitle.append("Owner")
        elif("ceo" in row["title"].lower()):
            newTitle.append("CEO")
        elif("cofounder" in row["title"].lower()):
            newTitle.append("Cofounder")
        elif("founder" in row["title"].lower()):
            newTitle.append("Founder")
        elif("co-founder" in row["title"].lower()):
            newTitle.append("Cofounder")
        elif("chief executive officer" in row["title"].lower()):
            newTitle.append("CEO")
        elif("chief executive" in row["title"].lower()):
            newTitle.append("CEO")
        elif("chef executive office" in row["title"].lower()):
            newTitle.append("CEO")
        elif('direktør og grundlægger' in row["title"].lower()):
            newTitle.append("Founder")
        elif('directrice et fondatrice' in row["title"].lower()):
            newTitle.append("Founder")
        elif('創業家' in row["title"].lower()):
            newTitle.append("Founder")
        elif('mede-oprichter' in row["title"].lower()):
            newTitle.append("Cofounder")
        elif('gründer' in row["title"].lower()):
            newTitle.append("Founder")
        elif('首席执行官' in row["title"].lower()):
            newTitle.append("CEO")
        elif('coo' in row["title"].lower()):
            newTitle.append("COO")
        elif('chief operating officer' in row["title"].lower()):
            newTitle.append("COO")
        elif('founding director' in row["title"].lower()):
            # Don't want directors - too low on the chain
            newTitle.append("Founding Director")
            dropIndices.append(index)
        elif('grundare' in row["title"].lower()):
            newTitle.append("Founder")
        elif(('cofundador' in row["title"].lower()) or
        ('co-fondateur' in row["title"].lower()) or
        ('cofondateur' in row["title"].lower()) or 
        ('cofondatrice' in row["title"].lower()) or
        ('co-fondatrice' in row["title"].lower()) or
        ('co-fondatore' in row["title"].lower()) or
        ('cofondatore' in row["title"].lower()) or
        ('co-fundador' in row["title"].lower()) or
        ('cofundador' in row["title"].lower())):
            newTitle.append("Cofounder")
        elif(('fondatrice' in row["title"].lower()) or
        ('oprichter' in row["title"].lower())):
            newTitle.append("Founder")
        else:
            newTitle.append(row["title"])

        # Drop assistant, member, research fellow, chief of staff, secretary
        if("assistant" in row["title"].lower()):
            dropIndices.append(index)
        elif("member" in row["title"].lower()):
            dropIndices.append(index)
        elif("research fellow" in row["title"].lower()):
            dropIndices.append(index)
        elif("chief of staff" in row["title"].lower()):
            dropIndices.append(index)
        elif("secretary" in row["title"].lower()):
            dropIndices.append(index)
        elif("personal wealth executive" in row["title"].lower()):
            dropIndices.append(index)


    df["title"] = newTitle
    df = df.drop(dropIndices)

    return df

# Check and see if the email is actually for this company
# Also remove any empty emails
def clean_emails(df):
    print("Before cleaning emails: ", df.shape)
    df = df[df["email"].notna()]
    df = df[df["email"] != ""]
    print("After cleaning emails: ", df.shape)
    return df

# drop nans from website links
def clean_website_links(df):
    print(df.shape)
    df = df[df["organization_website_url"].notna()]
    print(df.shape)
    return df

# Look at how the company is referenced in:
# website link, short desc, linkedin link...
# can use AI - actually only need to run this for the confusing ones!
# i.e. if the company name is different from the domain name or linkedin name
def clean_company_names(df):
    count = 0
    new_org_name = []
    apiCallCount = 0
    # print(df[df["organization_name"] == "DadGang Co."])
    # df = df[df["organization_name"] == "DadGang Co."]
    for index, row in df.iterrows():
        org_name = row["organization_name"]
        org_website = row["organization_website_url"]        

        # basic org name cleaning
        org_name = clean_single_company_name(org_name)
        org_name = org_name.lower()

        # basic website cleaning
        org_website = org_website.split("www.")[1]
        org_website = org_website.split(".")[0]
        org_website = org_website.lower()

        # corrected org name if no changes needed
        corrected_org_name = clean_single_company_name(row["organization_name"])
        
        # check if the org name equals the website
        if(org_name == org_website):
            count += 1
            new_org_name.append(corrected_org_name)
        else:
            if(not pd.isna(row["organization_short_description"])):
                # AI check
                prompt = '''What is the correct name of the company based on the short description
                in [short description] and the company name in [company name]? Return the name only
                and nothing else.

                [short description]
                <<short description>>
                [company name]
                <<company name>>
                '''

                prompt = prompt.replace("<<short description>>", row["organization_short_description"])
                prompt = prompt.replace("<<company name>>", row["organization_name"])
                llmOutput = llmCall(prompt)
                print("LLM Output: ", llmOutput, "Corrected: ", clean_single_company_name(llmOutput))
                count += 1
                new_org_name.append(clean_single_company_name(llmOutput))
                apiCallCount += 1
                time.sleep(1)
            else:
                new_org_name.append(corrected_org_name)

    print(count)
    print(df.shape)
    print(new_org_name)
    df["organization_name"] = new_org_name
    return df

def clean_single_company_name(org_name):
    corrected_org_name = org_name.replace("®", "").replace("™", "").replace("©", "")
    corrected_org_name = corrected_org_name.replace(", Inc.", "").replace("Inc.", "").replace(", Inc", "").replace("Inc", "").replace(",Inc.","").replace(",Inc","")
    corrected_org_name = corrected_org_name.replace(", LLC.", "").replace("LLC.", "").replace(", LLC", "").replace("LLC", "").replace(",LLC.","").replace(",LLC","")
    # "Co" is too common so cannot just replace it
    corrected_org_name = corrected_org_name.replace(", Co.", "").replace("Co.", "").replace(", Co", "").replace(",Co.", "").replace(",Co", "")
    corrected_org_name = corrected_org_name.replace(", Ltd.", "").replace("Ltd.", "").replace(", Ltd", "").replace("Ltd", "").replace(",Ltd.","").replace(",Ltd","")
    corrected_org_name = corrected_org_name.replace(", Pvt.", "").replace("Pvt.", "").replace(", Pvt", "").replace("Pvt", "").replace(",Pvt.","").replace(",Pvt","")

    if(corrected_org_name[-3:] == " Co"):
        corrected_org_name = corrected_org_name[:-3]
    elif(corrected_org_name[-4:] == ", Co"):
        corrected_org_name = corrected_org_name[:-4]

    corrected_org_name = corrected_org_name.strip()
    return corrected_org_name