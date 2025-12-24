import requests
import os
import pandas as pd
import time
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

def call_perplexity_api(prompt, model="sonar"):
    """
    Call Perplexity API to get a response
    """
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert at evaluating B2B leads and determining if they match an Ideal Customer Profile (ICP). Always respond with a score from 0-10 and a brief explanation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = response.json()
        except:
            error_detail = response.text
        print(f"Error calling Perplexity API: {e}")
        print(f"Response: {error_detail}")
        return None
    except Exception as e:
        print(f"Error calling Perplexity API: {e}")
        return None

def extract_score_from_response(response_text):
    """
    Extract a score (0-10) from the Perplexity response
    Looks for patterns like "Score: 8", "8/10", "rating: 7", etc.
    """
    if not response_text:
        return 5  # Default score if no response
    
    # Try to find a number between 0-10 in the response
    # Look for patterns like "Score: 8", "8/10", "rating of 7", etc.
    patterns = [
        r'score[:\s]+(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*/\s*10',
        r'rating[:\s]+(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*out\s*of\s*10',
        r'\b([0-9]|10)\b'  # Last resort: any number 0-10
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response_text.lower())
        if matches:
            try:
                score = float(matches[0])
                # Ensure score is between 0-10
                score = max(0, min(10, score))
                return round(score, 1)
            except ValueError:
                continue
    
    # If no score found, return default
    return 5.0

def create_icp_evaluation_prompt(lead_data):
    """
    Create a prompt to evaluate if a lead matches the ICP
    """
    # Helper function to safely get and format values
    def safe_get(key, default='N/A', max_len=None):
        value = lead_data.get(key, default)
        if pd.isna(value) or value == '' or value == 'nan':
            return default
        value_str = str(value)
        if max_len and len(value_str) > max_len:
            return value_str[:max_len] + '...'
        return value_str
    
    prompt = f"""Evaluate if this B2B lead matches our Ideal Customer Profile (ICP) and provide a score from 0-10.

Lead Information:
- Name: {safe_get('full_name')}
- Job Title: {safe_get('job_title')}
- Company: {safe_get('company_name')}
- Industry: {safe_get('industry')}
- Company Size: {safe_get('company_size')}
- Company Website: {safe_get('company_website')}
- Company Description: {safe_get('company_description', max_len=500)}
- Location: {safe_get('city')}, {safe_get('state')}, {safe_get('country')}
- Seniority Level: {safe_get('seniority_level')}
- Company Technologies: {safe_get('company_technologies', max_len=300)}

ICP Criteria (Temporary - to be refined):
- Target: E-commerce companies, SaaS businesses, or performance marketing agencies
- Decision makers: Founders, CEOs, C-suite executives, or senior marketing directors
- Company size: Preferably 10-500 employees (but flexible)
- Industry: E-commerce, retail, digital marketing, or related B2B services
- Technology stack: Should use modern e-commerce or marketing tools

Please evaluate this lead and provide:
1. A score from 0-10 (where 10 is a perfect ICP match)
2. A brief 1-2 sentence explanation

Format your response as: "Score: X/10 - [explanation]"
"""
    return prompt

def evaluate_leads_with_perplexity(file_path):
    """
    Read apollo_final.csv, evaluate each lead using Perplexity API,
    and add ICP score columns directly to the same file
    """
    print("Loading Apollo final leads...")
    df = pd.read_csv(file_path)
    print(f"Total leads to evaluate: {len(df)}")
    
    # Check if columns already exist, if so, only update missing scores
    if 'icp_score' not in df.columns:
        df['icp_score'] = None
    if 'icp_evaluation' not in df.columns:
        df['icp_evaluation'] = None
    
    # Process each lead (skip if already has a score)
    total_leads = len(df)
    leads_to_evaluate = df[df['icp_score'].isna() | (df['icp_score'] == '')].copy()
    leads_already_scored = total_leads - len(leads_to_evaluate)
    
    if leads_already_scored > 0:
        print(f"Skipping {leads_already_scored} leads that already have scores")
    
    for idx, (index, row) in enumerate(leads_to_evaluate.iterrows()):
        print(f"\nEvaluating lead {idx + 1}/{len(leads_to_evaluate)}: {row.get('full_name', 'N/A')} at {row.get('company_name', 'N/A')}")
        
        # Create evaluation prompt
        prompt = create_icp_evaluation_prompt(row.to_dict())
        
        # Call Perplexity API
        response = call_perplexity_api(prompt)
        
        if response:
            # Extract score
            score = extract_score_from_response(response)
            df.at[index, 'icp_score'] = score
            df.at[index, 'icp_evaluation'] = response[:500]  # Store first 500 chars of evaluation
            
            print(f"  Score: {score}/10")
            print(f"  Evaluation: {response[:200]}...")
        else:
            df.at[index, 'icp_score'] = 5.0  # Default score on error
            df.at[index, 'icp_evaluation'] = "Error: Could not evaluate"
            print(f"  Error: Could not get evaluation, using default score 5.0")
        
        # Rate limiting - wait 1 second between requests to avoid hitting API limits
        if idx < len(leads_to_evaluate) - 1:  # Don't wait after last request
            time.sleep(1)
    
    # Sort by score (highest first)
    df = df.sort_values(by='icp_score', ascending=False, na_position='last')
    
    # Save back to the same file (overwrite)
    df.to_csv(file_path, index=False)
    print(f"\nCompleted! Updated {len(df)} leads with ICP scores in {file_path}")
    print(f"Score distribution:")
    print(df['icp_score'].describe())
    
    return df

