import pandas as pd


# Finds which companies were missing from apollo to see if they are covered in hunter/other sources

# 1. Read in the target companies
target_companies = pd.read_csv('inputs/[Done]_All-Live-Richpanel-Sites.csv', skiprows=1)

# companies = target_companies['Company Name'].tolist()
# 2. Read in the apollo companies
apollo_companies = pd.read_csv('outputs/apollo_richpanel.csv')
apollo_companies['clean_domain'] = (
    apollo_companies['organization_website_url']
    .str.replace(r'^https?:\/\/(www\.)?', '', regex=True)  # Remove http://, https://, www.
    .str.strip('/')  # Remove trailing slash
)

# 3. Find domains in target companies not in apollo
missing_domains = target_companies[~target_companies['Domain'].isin(apollo_companies['clean_domain'])]

# 4. Find the missing companies
print(missing_domains)

# 5. Write the domains to a txt file
with open('outputs/apollo_missing_domains.csv', 'w') as f:
    for domain in missing_domains['Domain']:
        f.write(domain + "," '\n')
# print(missing_companies)