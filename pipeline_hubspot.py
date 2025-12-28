from toolkit.hubspotFuncs import get_contacts

INPUT_DIR = 'inputs'
OUTPUT_DIR = 'outputs'
PROMPTS_DIR = 'prompts'


#Output file path -Step 16 : Hubspot lead pull
output_hubspot_leads = f'{OUTPUT_DIR}/hubspot_leads.csv'

skip=[0]


if 0 not in skip:
    get_contacts(output_hubspot_leads)
            
        