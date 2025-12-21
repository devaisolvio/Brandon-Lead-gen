# Automated Lead Generation Pipeline - Documentation

## Project Overview

This is an **Automated Lead Generation Pipeline** designed for AiSolv. It's a sophisticated system that automates the process of finding, qualifying, enriching, and personalizing sales leads from e-commerce companies (specifically targeting D2C and Shopify-based businesses). The system uses multiple data sources, AI enrichment, and email outreach platforms to manage a lead acquisition workflow.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [The 12-Step Pipeline](#the-12-step-pipeline)
4. [Toolkit Modules](#toolkit-modules)
5. [Architecture & Data Flow](#architecture--data-flow)
6. [Key Integrations & APIs](#key-integrations--apis)
7. [Configuration & Execution](#configuration--execution)
8. [Data Quality Assurance](#data-quality-assurance-features)
9. [Output Files](#output-files-explained)
10. [Security Notes](#security-notes)

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- API accounts for the following services:
  - OpenAI (GPT-4.1)
  - NeverBounce
  - Instantly.ai
  - BrightData
  - Apify (for Apollo.io scraping)
  - Supabase (optional)

### Installation

1. **Clone or download the repository**

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:

Copy the `.env.example` file to create your own `.env` file:
```bash
cp .env.example .env
```

4. **Configure your API keys**:

Open the `.env` file and add your actual API keys:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_actual_openai_api_key_here

# NeverBounce API Configuration
NEVERBOUNCE_API_KEY=your_actual_neverbounce_api_key_here

# Instantly.ai API Configuration
INSTANTLY_API_KEY=your_actual_instantly_api_key_here

# BrightData API Configuration
BRIGHTDATA_BEARER_TOKEN=your_actual_brightdata_token_here

# Supabase Configuration
SUPABASE_URL=your_actual_supabase_url_here
SUPABASE_SERVICE_ROLE_KEY=your_actual_supabase_key_here

# Apify API Configuration
APIFY_API_TOKEN=your_actual_apify_token_here
```

**Where to get your API keys**:
- **OpenAI**: https://platform.openai.com/api-keys
- **NeverBounce**: https://app.neverbounce.com/settings/api
- **Instantly.ai**: https://app.instantly.ai/app/settings/integrations
- **BrightData**: https://brightdata.com/cp/api_access
- **Supabase**: https://app.supabase.com/project/_/settings/api
- **Apify**: https://console.apify.com/account/integrations

5. **Prepare your input data**:

Place your BuiltWith CSV files in the `/inputs/` directory.

6. **Run the pipeline**:

```bash
python pipeline_importing.py
```

### Important Security Notes

- **NEVER commit the `.env` file to version control** - it contains sensitive API keys
- The `.gitignore` file is configured to exclude `.env` automatically
- Share the `.env.example` file with team members, not the actual `.env` file
- Each team member should create their own `.env` file with their API keys

---

## Project Structure

### Root-Level Files

**`pipeline_importing.py`** (Main Orchestrator - 410 lines)
- Central control hub of the entire system
- Defines 12 sequential steps that orchestrate the lead generation pipeline
- Contains all workflow functions and configuration
- Uses a `skip` array to control which steps are executed

### Input Data Files (`/inputs/` directory)

Contains **40+ CSV files** from various data sources:
- BuiltWith technology stacks (Klaviyo, Shopify Plus, TikTok Pixel sites, etc.)
- Pre-processed lists of e-commerce companies filtered by technology usage
- File sizes range from 21KB to 291MB (very large datasets)

### Output Files (`/outputs/` directory)

Stores intermediate and final results:
- Processed leads at various stages of the pipeline
- Verified and cleaned lead lists
- Analytics data from email outreach

### Toolkit Directory (`/toolkit/`)

Contains modular support functions for API integrations, data cleaning, scraping, and enrichment.

### Prompts Directory (`/prompts/performance_marketers/`)

Contains AI prompt templates for:
- `generate_personalizations.txt` - Generates 10 personalization variants
- `select_one.txt` - Selects the best personalization from generated options

---

## The 12-Step Pipeline

### Step 0: Export Instantly Leads

**File**: `toolkit/instantlyFuncs.py`

**Purpose**: Pulls all leads that have already been contacted via the Instantly.ai email outreach platform

**Process**:
- Calls Instantly.ai API with pagination
- Retrieves all previously contacted leads

**Output**: `instantly_leads.csv`

**Why**: Prevents duplicate outreach to people who've already been contacted

---

### Step 1: Filter BuiltWith Companies by Instantly Companies

**Function**: `filter_builtwith_companies_by_instantly_companies()`

**Purpose**: Removes companies that have already been contacted from the BuiltWith lead source

**Process**:
- Cross-references company names and domains
- Eliminates duplicates between BuiltWith data and Instantly contacts

**Output**: `builtwith_filtered_leads.csv` (only new companies)

---

### Step 2: Extract Company Domains for Apollo

**Function**: `import_leads_from_builtwith()`

**Purpose**: Converts the filtered company list into a format that can be imported into Apollo.io

**Process**:
- Extracts domain URLs from filtered companies
- Formats them as newline-separated list

**Output**: `importList.txt` (list of domain URLs)

---

### Step 3: Apollo Scraping

**File**: `toolkit/apolloFuncs.py`

**Purpose**: Uses the Apify Apollo.io scraper to extract contact information

**Process**:
- Sends domains to Apify's Apollo scraper endpoint
- Targets: Founders, CEOs, Co-founders (based on Apollo filter)
- Uses Apollo.io as B2B contact database

**Output**: `apollo.csv` (raw contact data with emails)

---

### Step 4: Clean Apollo Data

**File**: `toolkit/cleaning.py` (189 lines)

**Purpose**: Cleans and standardizes the raw Apollo data

**Operations**:

1. **Title Cleaning**:
   - Normalizes job titles across 20+ languages
   - Handles: CEO, Founder, Cofounder, COO, Owner
   - Languages: English, Danish, French, Dutch, Swedish, German, Spanish, Chinese, and more

2. **Email Validation**:
   - Removes empty/null emails
   - Validates email format

3. **Website Link Cleaning**:
   - Removes rows missing website URLs

4. **Company Name Cleaning**:
   - Removes trademark symbols (®, ™, ©)
   - Removes legal suffixes (Inc., LLC., Ltd., Pvt., Co.)
   - Uses OpenAI API (GPT-4.1) for ambiguous cases to validate correct company names

**Output**: `Secondary_Tier_1.csv` (cleaned data)

---

### Step 5: Recheck Duplicate Emails

**Function**: `recheck_duplicate_emails()`

**Purpose**: Removes any contacts who've already been reached in the Instantly leads

**Process**:
- Case-insensitive string matching on email addresses
- Compares against Instantly export from Step 0

**Output**: `rechecked_duplicates.csv`

---

### Step 6: AI-Powered E-Commerce Filtering

**File**: `toolkit/scrapeAIFuncs.py`

**Purpose**: Uses AI to filter out non-e-commerce companies

**Process**:
- Analyzes company descriptions with OpenAI GPT-4.1
- Asks: "Is this an e-commerce/D2C company?"
- Uses generous criteria (accepts physical products, strict on pure services)
- Delays 0.25 seconds between API calls (rate limiting)

**Output**: `rechecked_duplicates.csv` (only e-commerce companies)

---

### Step 7: Email Verification

**File**: `toolkit/neverBounceHTTP.py`

**Purpose**: Verifies that email addresses are valid and active

**Tool**: NeverBounce API (email verification service)

**Process**:
1. Converts email list to NeverBounce format
2. Submits batch job to API
3. Polls job status every 15 seconds until complete
4. Downloads verified results
5. Filters to only valid emails

**Output**:
- `verified.csv` (only valid emails)
- `verified_subsetted.csv` (merged with original data)

---

### Step 8: Insert Into Leads Bank

**Function**: `insert_into_leads_bank()`

**Purpose**: Stores verified leads in a persistent "leads bank" CSV

**Logic**:
- Deduplicates within the new batch
- Removes emails that already exist in the bank
- **If new contact at existing company**: copies company cooloff date (14-day cooloff)
- **If brand new company**: sets cooloff date to 2020-01-01 (immediately available)

**Purpose of Cooloff**: Prevents spamming the same company repeatedly

**Output**: `leads_bank.csv` (persistent database)

---

### Step 9: Retrieve Leads from Leads Bank

**Function**: `retrieve_leads_from_leads_bank()`

**Purpose**: Pulls leads ready for outreach from the leads bank

**Selection Logic**:
- Only retrieves leads where company cooloff date has passed
- Updates cooloff date to today + 14 days for all contacts at that company
- Removes retrieved leads from bank
- Iterates one-at-a-time to check dates properly

**Output**: `rechecked_duplicates.csv` (leads ready to contact)

---

### Step 10: Check Against Previous Customers

**Functions**: `check_against_previous_customers()`, `clean_previous_customers()`

**Purpose**: Prevents outreach to companies who are already customers

**Input**: `Previous_Customers_and_Samples_Given.csv`

**Process**:
- Normalizes URLs and company names for matching
- Filters out companies in previous customer list
- Filters out companies already contacted via Instantly

**Output**: `rechecked_previous_customers.csv`

---

### Step 11: Add Company Technology Stack

**Function**: `add_company_tech_column()`

**File**: `toolkit/getCompanyTech.py`

**Purpose**: Enriches leads with the technology stack each company uses

**Data Source**: `grouped_by_domain.csv` (created by combining all input files)

**Combination Process**:
1. Reads all CSV files from `/inputs/` directory
2. Each file represents companies using a specific technology (e.g., Klaviyo, Shopify Plus, Postscript)
3. Groups by domain and creates lists of technologies per company

**Output**: `final_leads_with_tech.csv` (leads + their tech stacks)

---

### Step 12: LinkedIn Enrichment & AI Personalization

**File**: `toolkit/linkedInScraper.py` (194 lines)

**Purpose**: Scrapes LinkedIn profiles and generates personalized outreach messages

**Sub-Process**:

#### 12a: LinkedIn Scraping
- Uses BrightData API to scrape LinkedIn profiles
- Extracts public profile data for each founder/CEO
- Queues URLs for scraping
- Polls until complete (timeout: 60 minutes)

#### 12b: Generate Personalizations (AI)
- Uses prompts from `/prompts/performance_marketers/generate_personalizations.txt`
- OpenAI GPT-4.1 generates 10 personalization variations for each lead
- Based on:
  - Dynamic compliments (product, growth, achievements)
  - Specific observations (location, education, achievements)
  - Achievement callouts (awards, milestones, opportunities)

#### 12c: Select Best Personalization (AI)
- Uses prompt from `/prompts/performance_marketers/select_one.txt`
- OpenAI agent selects the single best personalization from the 10 generated
- Expert persona: "10-year email outreach sales agent"
- Goal: Highest probability of customer interest

**Output**: `linkedin_enriched_leads.csv` (leads + personalized outreach messages)

---

## Toolkit Modules

### Core Modules

| File | Purpose | Key Functions |
|------|---------|---------------|
| **`apolloFuncs.py`** | Apollo.io scraping via Apify | Sends API request to Apify Apollo scraper |
| **`cleaning.py`** | Data cleaning and standardization | Cleans titles, emails, websites, company names (AI-assisted) |
| **`instantlyFuncs.py`** | Instantly.ai integration | Exports already-contacted leads |
| **`instantlyAnalytics.py`** | Campaign analytics | Pulls analytics on lead interest/engagement from Instantly |
| **`neverBounceHTTP.py`** | Email verification | Batch email verification using NeverBounce API |
| **`linkedInScraper.py`** | LinkedIn + personalization | Scrapes LinkedIn profiles, generates personalized messages via AI |
| **`scrapeAIFuncs.py`** | AI filtering | Filters non-e-commerce companies using AI |
| **`getCompanyTech.py`** | Technology enrichment | Combines all tech stack CSVs into domain-indexed database |
| **`supabaseFuncs.py`** | Database operations | Insert, retrieve leads with cooloff logic |
| **`llmFuncs.py`** | AI API wrapper | OpenAI GPT-4.1 API wrapper for all AI calls |

### Additional Modules

| File | Purpose |
|------|---------|
| **`personalization.py`** | Facebook ads scraping (currently unused) |
| **`randomSelect.py`** | Randomly samples leads from lists |
| **`findMissingEmails.py`** | Finds companies missing from Apollo for other sources |
| **`verifyEmails.py`** | (Empty file) |

---

## Architecture & Data Flow

```
┌─────────────────────────────────────────────────────┐
│  INPUTS (40+ BuiltWith CSV Files)                   │
│  - Klaviyo users, Shopify Plus, TikTok Pixel, etc. │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 0: Export Instantly Leads                     │
│  (Already contacted - for deduplication)            │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 1: Filter against Instantly contacts          │
│  (Remove duplicates)                                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 2: Extract domains to import list             │
│  (Format for Apollo)                                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 3: Apollo.io Scraping                         │
│  (Extract founder/CEO contacts via Apify)           │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 4: Data Cleaning                              │
│  (Titles, emails, websites, company names + AI)     │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 5: Recheck for duplicates with Instantly      │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 6: AI Filter for E-Commerce companies         │
│  (GPT-4 powered filtering)                          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 7: Email Verification                         │
│  (NeverBounce API - validate email addresses)       │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 8: Insert into Leads Bank                     │ not req
│  (Persistent storage with 14-day cooloff)           │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 9: Retrieve available leads from bank         │
│  (Check cooloff dates, update for next cycle)       │not needed
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 10: Filter against previous customers         │
│  (Avoid contacting existing clients)                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 11: Enrich with company technology stack      │
│  (Add Shopify/Klaviyo/etc tech info)                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Step 12: LinkedIn scraping + AI personalization    │
│  (Generate custom outreach messages)                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  OUTPUTS                                            │
│  - final_leads_with_tech.csv                        │
│  - linkedin_enriched_leads.csv                      │
└─────────────────────────────────────────────────────┘
```

---

## Key Integrations & APIs

| Service | Purpose | Auth Method | Usage |
|---------|---------|-------------|-------|
| **Apollo.io** (via Apify) | B2B contact database scraping | Apify API token | Step 3: Extract founder/CEO emails |
| **OpenAI GPT-4.1** | AI data cleaning & personalization | API key | Steps 4, 6, 12: Clean data, filter companies, personalize |
| **NeverBounce** | Email verification | API key | Step 7: Validate email addresses |
| **Instantly.ai** | Email outreach platform | API key | Steps 0, 5, 10: Track contacted leads |
| **BrightData** | LinkedIn profile scraping | Bearer token | Step 12: Scrape LinkedIn profiles |
| **Supabase** | Lead database (alternative storage) | URL + Service key | Steps 8-9: Store/retrieve leads with cooloff |

---

## Configuration & Execution

### Skip Array Control

The pipeline is controlled by a **skip array** in `pipeline_importing.py`:

```python
skip = [0,1,2,3,4,5,6,7,8,9,10,11,12]
```

**How it works**:
- Numbers **in the array**: steps that are **SKIPPED**
- Numbers **NOT in array**: steps that **RUN**
- Allows selective execution without reprocessing entire pipeline

**Example**: To run only steps 3, 4, and 5:
```python
skip = [0,1,2,6,7,8,9,10,11,12]  # Only 3,4,5 will run
```

### Running the Pipeline

```bash
python pipeline_importing.py
```

The script will execute all non-skipped steps in sequence.

---

## Data Quality Assurance Features

### 1. Multi-Layer Duplicate Prevention

**Email-based deduplication**:
- Case-insensitive matching
- Whitespace trimming
- Cross-reference with Instantly contacts (Steps 0, 1, 5)
- Internal bank deduplication (Step 8)

**Company-based deduplication**:
- 14-day cooloff period between contacts (Steps 8-9)
- Previous customer checks (Step 10)

### 2. Email Validation

**NeverBounce API** (Step 7):
- Validates email format
- Checks if mailbox exists
- Verifies domain is active
- Filters out invalid/risky emails

### 3. Company Filtering

**Manual technology lists** (40+ CSV files):
- Pre-filtered by BuiltWith technology usage
- Targets Shopify, Klaviyo, TikTok Pixel users

**AI filtering** (Step 6):
- GPT-4 analyzes company descriptions
- Filters out consulting/services companies
- Focuses on D2C and e-commerce businesses

### 4. Title Standardization

**Multi-language support** (Step 4):
- Handles 20+ languages (English, Danish, French, Dutch, Swedish, German, Spanish, Chinese, etc.)
- Normalizes variations of CEO, Founder, Co-founder, COO, Owner
- Ensures consistent role identification

### 5. Intelligent Cooloff System

**14-day company-level cooloff**:
- Prevents spamming the same company
- Applies to ALL contacts at a company
- Automatically manages timing (Steps 8-9)

---

## Output Files Explained

| File | Stage | Contains | Purpose |
|------|-------|----------|---------|
| `instantly_leads.csv` | Step 0 | Already contacted leads | Deduplication reference |
| `builtwith_filtered_leads.csv` | Step 1 | New leads from BuiltWith | Filtered input data |
| `importList.txt` | Step 2 | Domain URLs | Apollo import format |
| `apollo.csv` | Step 3 | Raw Apollo data | Contact information |
| `Secondary_Tier_1.csv` | Step 4 | Cleaned Apollo data | Standardized contacts |
| `rechecked_duplicates.csv` | Steps 5,6,9 | Deduplicated leads | Various stages |
| `verified.csv` | Step 7 | Email verification results | Valid emails only |
| `verified_subsetted.csv` | Step 7 | Cleaned + verified leads | Ready for bank |
| `leads_bank.csv` | Step 8 | Master lead database | Persistent storage with cooloff |
| `rechecked_previous_customers.csv` | Step 10 | New leads after customer filter | Non-customer leads |
| `final_leads_with_tech.csv` | Step 11 | Leads with tech stacks | Enriched data |
| `linkedin_enriched_leads.csv` | Step 12 | Final leads + personalization | **FINAL OUTPUT - Ready to send** |
| `grouped_by_domain.csv` | Step 11 | Technology index | Company tech stacks |

### Key Output Files

**Most Important**:
- `linkedin_enriched_leads.csv` - Final output with personalized messages
- `final_leads_with_tech.csv` - Enriched leads ready for manual outreach
- `leads_bank.csv` - Persistent lead storage with cooloff management

---

## Notable Features

### 1. Intelligent Cooloff System
- **14-day cooloff per company** prevents spam
- Company-level (not contact-level) to avoid multiple touches
- Automatically managed through leads bank

### 2. Multi-Language Support
- Title cleaning handles **20+ languages**
- Supports: English, Danish, French, Dutch, Swedish, German, Spanish, Chinese, Norwegian, Portuguese, Italian, Polish, Russian, Japanese, Korean, Arabic, Turkish, Hindi, Thai

### 3. AI-Powered Quality Control
- **GPT-4.1** cleans ambiguous company names
- Filters out non-e-commerce businesses
- Generates personalized outreach messages
- Selects best personalization from 10 variants

### 4. Personalization at Scale
- Each lead gets **custom AI-generated message**
- Based on LinkedIn profile analysis
- 10 variants generated, best one selected
- Increases engagement rates

### 5. Graceful Error Handling
- Missing LinkedIn profiles don't break pipeline
- API rate limiting with delays
- Pagination handling for large datasets (100k+ records)
- Timeout protection (60-minute max for scraping)

### 6. Comprehensive Data Enrichment
- Technology stack (Shopify, Klaviyo, etc.)
- LinkedIn profile data
- Email verification status
- Company size and industry
- Founder/CEO contact information

---

## Security Notes

### Environment Variables

All API keys and sensitive credentials are now stored securely in environment variables using the `.env` file. The codebase has been updated to use the `python-dotenv` package to load these variables.

**API keys are loaded from the `.env` file**:
- OpenAI (GPT-4.1) - `OPENAI_API_KEY`
- NeverBounce - `NEVERBOUNCE_API_KEY`
- Instantly.ai - `INSTANTLY_API_KEY`
- BrightData - `BRIGHTDATA_BEARER_TOKEN`
- Supabase - `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
- Apify - `APIFY_API_TOKEN`

**Implementation example**:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
```

### Files Using Environment Variables

All toolkit files now load credentials from environment variables:
- `toolkit/llmFuncs.py` - OpenAI API key
- `toolkit/neverBounceHTTP.py` - NeverBounce API key
- `toolkit/instantlyFuncs.py` - Instantly.ai API key
- `toolkit/linkedInScraper.py` - BrightData token
- `toolkit/supabaseFuncs.py` - Supabase credentials
- `toolkit/apolloFuncs.py` - Apify API token

### Security Best Practices

1. **Never commit `.env` to version control**
   - The `.gitignore` file excludes `.env` automatically
   - Only commit `.env.example` with placeholder values

2. **Rotate API keys regularly**
   - Change keys if they may have been compromised
   - Use different keys for development and production

3. **Limit API key permissions**
   - Use read-only keys where possible
   - Restrict API key access to specific IP addresses when supported

4. **Monitor API usage**
   - Check for unusual activity in API dashboards
   - Set up billing alerts to detect unauthorized usage

---

## System Requirements

### Python Dependencies

Install all dependencies using:
```bash
pip install -r requirements.txt
```

The `requirements.txt` file includes:
```
pandas
requests
openai
python-dotenv
supabase
numpy
```

**Note**: `time`, `json`, `re`, and `os` are built-in Python modules and don't need to be installed.

### External Services Required

- Apollo.io account (via Apify)
- OpenAI API access (GPT-4.1)
- NeverBounce account
- Instantly.ai account
- BrightData subscription
- Supabase project (optional)

---

## Maintenance & Monitoring

### Regular Maintenance Tasks

1. **Update BuiltWith data** - Refresh CSV files in `/inputs/` directory
2. **Monitor API quotas** - Check usage for OpenAI, NeverBounce, BrightData
3. **Clean leads bank** - Periodically review `leads_bank.csv` for stale data
4. **Update previous customers** - Keep `Previous_Customers_and_Samples_Given.csv` current
5. **Review email verification results** - Monitor bounce rates and verification accuracy

### Monitoring Metrics

- **Lead conversion rate** - Track from Instantly.ai analytics
- **Email verification pass rate** - Monitor NeverBounce results
- **AI filtering accuracy** - Review e-commerce classification
- **Personalization effectiveness** - Track response rates by personalization type
- **Cooloff compliance** - Ensure no companies contacted within 14 days

---

## Troubleshooting

### Common Issues

**Pipeline stops mid-execution**:
- Check API rate limits
- Verify API keys are valid
- Review error logs for timeout issues

**Duplicate emails appearing**:
- Verify Step 0 exported Instantly leads correctly
- Check email normalization (case, whitespace)
- Review leads bank deduplication logic

**Low email verification pass rate**:
- Review Apollo data quality
- Check if domains are active
- Consider adjusting Apollo filters

**Poor AI filtering results**:
- Review company descriptions quality
- Adjust AI prompt criteria
- Increase delay between API calls if rate limited

**LinkedIn scraping fails**:
- Check BrightData API status
- Verify URL format
- Review timeout settings (60 min default)

---

## Future Enhancements

### Potential Improvements

1. **Environment variables** - Move all API keys to `.env` file
2. **Error recovery** - Add checkpoint/resume functionality
3. **Parallel processing** - Speed up AI operations with async/threading
4. **Real-time monitoring** - Dashboard for pipeline status
5. **A/B testing framework** - Test different personalization strategies
6. **Webhook notifications** - Alert on pipeline completion/errors
7. **Database migration** - Move from CSV to proper database (PostgreSQL/Supabase)
8. **Logging enhancement** - Structured logging with log levels
9. **Unit tests** - Add test coverage for critical functions
10. **Configuration file** - Move settings to YAML/JSON config

---

## Contact & Support

For questions or issues with this pipeline, contact the AiSolv development team.

---

**Last Updated**: 2025-12-18

**Version**: 1.0

**Maintained By**: AiSolv Team



### Requirements
Timeline for the Development of a Python-based automated lead generation and outreach system:
Week 1: Infrastructure Setup
- Set up Infrastructure - Instantly Warmup, Domains, Email Addresses, DKIM/DMARC Records...
- System architecture Design
- Prompts and processes to qualify target leads based on defined ICP criteria
Week 2: Lead Processing Pipeline Development Part 1
- Lead scraping workflow
- Lead cleaning workflow
- DNC list checking / deduplication
Week 3: Lead Processing Pipeline Development Part 2
- Lead qualification workflow
- Bounce verification checker
- Hubspot Integration (CRM updates and for reengaging previous leads)
Week 4: Linkedin Outreach, System Testing, and Campaign Development
- Integration with HeyReach for multichannel outreach
- End-to-end testing of each step in our systems
- Creating the messaging for our campaigns
Week 5: Instantly Domains Warmed up
- Email accounts should be warmed up and ready to go
- Commence sending emails - pyramid up the sending volume (increasing by 1 email sent every week day)

### Steps of the Pipeline

Step0-Exporting leads from instantly 
Step1-scraping
set2-cleaning
step3-dnc checking
ste4-lead qualification
step5- bounce verification
step6-lead enrichment


