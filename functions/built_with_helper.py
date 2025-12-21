import pandas as pd



# Input a file with builtwith leads and then make the list of the domain url simpler 
def import_leads_from_builtwith(builtwith_leads_file_path, output_import_list_file_path):
    df = pd.read_csv(builtwith_leads_file_path)
    output = str(list(df["Domain"])).replace("'", "").replace("[", "").replace("]", "").replace(" ", "\n")
    with open(output_import_list_file_path, 'w') as f:
        f.write(output)



## Filtering the leads of built with with instantly lead and return only the leads which are not contacted
def filter_builtwith_companies_by_instantly_companies(builtwith_leads_file_path, output_instantly_leads_file_path, output_builtwith_filtered_leads_file_path):
    df_instantly = pd.read_csv(output_instantly_leads_file_path)
    df_builtwith = pd.read_csv(builtwith_leads_file_path, skiprows=1)

    df_instantly = df_instantly[["company_domain", "email", "company_name"]]
    df_builtwith = df_builtwith[["Domain", "Company", "Emails"]]

    prexisting_company_names = df_instantly["company_name"].values
    prexisting_company_names = prexisting_company_names[~pd.isna(prexisting_company_names)]
    prexisting_company_names = [name.lower() for name in prexisting_company_names]

    prexisting_company_domains = df_instantly["company_domain"].values
    prexisting_company_domains = prexisting_company_domains[~pd.isna(prexisting_company_domains)]
    prexisting_company_domains = [domain.lower() for domain in prexisting_company_domains]

    indices_subset = []
    for index, new_lead in df_builtwith.iterrows():
        # adds to subset if company info not in prexisting company info
        if not pd.isna(new_lead["Company"]):
            if new_lead["Company"].lower() in prexisting_company_names:
                continue
        if not pd.isna(new_lead["Domain"]):
            if new_lead["Domain"].lower() in prexisting_company_domains:
                continue

        indices_subset.append(index)

    df_builtwith = df_builtwith.iloc[indices_subset]
    df_builtwith.to_csv(output_builtwith_filtered_leads_file_path, index=False)    