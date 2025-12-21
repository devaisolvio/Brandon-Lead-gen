# How to Run the Lead Generation Pipeline

## Quick Start (Run Everything)

To run the **entire 12-step pipeline** from start to finish:

1. **Open** `pipeline_importing.py`

2. **Find line 379** which looks like:
```python
skip = [0,1,2,3,4,5,6,7,8,9,10,11,12]
```

3. **Change it to an empty array** to run all steps:
```python
skip = []
```

4. **Run the pipeline**:
```bash
python pipeline_importing.py
```

---

## Understanding the Skip Array

The `skip` array controls which steps to run:

- **Numbers IN the array** = steps that are **SKIPPED**
- **Numbers NOT in the array** = steps that **RUN**

### Examples

**Run everything:**
```python
skip = []
```

**Skip everything (do nothing):**
```python
skip = [0,1,2,3,4,5,6,7,8,9,10,11,12]  # Current default
```

**Run only steps 3, 4, and 5:**
```python
skip = [0,1,2,6,7,8,9,10,11,12]
```

**Skip only step 12 (LinkedIn enrichment):**
```python
skip = [12]
```

---

## The 12 Pipeline Steps

| Step | Name | What It Does | Typical Use |
|------|------|--------------|-------------|
| **0** | Export Instantly Leads | Downloads already-contacted leads from Instantly.ai | Always run first |
| **1** | Filter BuiltWith Companies | Removes duplicates from BuiltWith data | Always run after Step 0 |
| **2** | Extract Domains | Creates domain list for Apollo | Always run after Step 1 |
| **3** | Apollo Scraping | Scrapes contact info from Apollo.io | Run when you have new domains |
| **4** | Clean Apollo Data | Cleans titles, emails, company names | Always run after Step 3 |
| **5** | Recheck Duplicates | Removes duplicate emails | Always run after Step 4 |
| **6** | AI E-commerce Filter | Filters non-e-commerce companies | Run to improve lead quality |
| **7** | Email Verification | Verifies emails via NeverBounce | Always run before Step 8 |
| **8** | Insert into Leads Bank | Stores leads with cooloff periods | Always run after Step 7 |
| **9** | Retrieve from Leads Bank | Gets leads ready for outreach | Run when ready to send emails |
| **10** | Check Previous Customers | Filters out existing customers | Always run after Step 9 |
| **11** | Add Tech Stack | Enriches with technology data | Run to add tech info |
| **12** | LinkedIn Enrichment | Scrapes LinkedIn + AI personalization | Run for personalized outreach |

---

## Common Workflows

### 1. First Time Running (Full Pipeline)
```python
skip = []  # Run all steps
```
**Note:** Step 3 will prompt you to paste an Apollo URL.

### 2. Processing New Leads Only
```python
skip = [0,1,2]  # Skip initial filtering, start from Apollo scraping
```

### 3. Skip LinkedIn (Faster Processing)
```python
skip = [12]  # Skip LinkedIn enrichment, everything else runs
```

### 4. Only Add Tech Stack to Existing Leads
```python
skip = [0,1,2,3,4,5,6,7,8,9,10,12]  # Only run Step 11
```

### 5. Resume After Email Verification
```python
skip = [0,1,2,3,4,5,6,7]  # Start from Step 8 (leads bank)
```

---

## Step-by-Step First Run

### Prerequisites Checklist

Before running, ensure:

- [ ] Python dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file configured with API keys
- [ ] BuiltWith CSV files in `/inputs/` directory
- [ ] `Previous_Customers_and_Samples_Given.csv` exists in `/inputs/`
- [ ] Apollo.io account ready (for Step 3)

### Running Your First Pipeline

**Step 1:** Edit `pipeline_importing.py`

Find line **357** and update the input file:
```python
input_builtwith_leads_file_path = 'inputs/YOUR_BUILTWITH_FILE.csv'
```

**Step 2:** Configure which steps to run

For first run, I recommend starting with steps 0-7:
```python
skip = [8,9,10,11,12]  # Run Steps 0-7 (filtering, scraping, cleaning, verifying)
```

**Step 3:** Run the pipeline
```bash
python pipeline_importing.py
```

**Step 4:** Monitor progress

Watch the console output. The pipeline will:
- Export Instantly leads
- Filter BuiltWith data
- Create import list
- **Prompt for Apollo URL** (Step 3) - Paste your Apollo filter URL
- Clean data
- Recheck duplicates
- AI filter e-commerce
- Verify emails

**Step 5:** Check outputs

After completion, check the `/outputs/` directory:
- `instantly_leads.csv` - Previously contacted leads
- `builtwith_filtered_leads.csv` - New leads
- `apollo.csv` - Contact info from Apollo
- `Secondary_Tier_1.csv` - Cleaned data
- `verified_subsetted.csv` - Verified emails

**Step 6:** Run remaining steps

Once Steps 0-7 complete successfully, run the rest:
```python
skip = [0,1,2,3,4,5,6,7]  # Run Steps 8-12
```

```bash
python pipeline_importing.py
```

---

## Important Notes About Step 3 (Apollo Scraping)

**Step 3 is INTERACTIVE** - it will pause and ask you to:

1. Log into Apollo.io
2. Set up your filters (CEO, Founder, etc.)
3. Copy the URL from your browser
4. Paste it into the terminal

**Example Apollo URL:**
```
https://app.apollo.io/#/people?page=1&personTitles[]=founder&personTitles[]=cofounder&personTitles[]=ceo...
```

The script will automatically scrape contacts based on the domains in your import list.

---

## Checking Which Steps Are Commented Out

**IMPORTANT:** Lines 384-387 in the pipeline have some issues:

```python
if 0 not in skip:
    export_instantly_leads(-1)
#if 1 not in skip:  # <-- Step 1 condition is commented out!
    filter_builtwith_companies_by_instantly_companies(...)
#if 2 not in skip:  # <-- Step 2 condition is commented out!
    import_leads_from_builtwith(...)
```

**This means Steps 1 and 2 will ALWAYS run** regardless of the skip array!

If you want proper control, uncomment these lines:
```python
if 0 not in skip:
    export_instantly_leads(-1)
if 1 not in skip:  # Fixed
    filter_builtwith_companies_by_instantly_companies(...)
if 2 not in skip:  # Fixed
    import_leads_from_builtwith(...)
```

---

## Output Files Reference

After running the pipeline, you'll find these files in `/outputs/`:

| File | Created by Step | Description |
|------|-----------------|-------------|
| `instantly_leads.csv` | 0 | Previously contacted leads |
| `builtwith_filtered_leads.csv` | 1 | Filtered company list |
| `importList.txt` | 2 | Domain list for Apollo |
| `apollo.csv` | 3 | Raw Apollo data |
| `Secondary_Tier_1.csv` | 4 | Cleaned data |
| `rechecked_duplicates.csv` | 5,6,9 | Various stages |
| `verified.csv` | 7 | Email verification results |
| `verified_subsetted.csv` | 7 | Verified + cleaned data |
| `leads_bank.csv` | 8 | Persistent lead storage |
| `rechecked_previous_customers.csv` | 10 | After customer filter |
| `final_leads_with_tech.csv` | 11 | With tech stack data |
| `linkedin_enriched_leads.csv` | 12 | **FINAL OUTPUT** |

---

## Troubleshooting

### Pipeline won't run
**Check:**
- Is the `skip` array configured correctly?
- Are your input files in the `/inputs/` directory?
- Are environment variables loaded? Run: `python test_env_vars.py`

### Step 3 fails
**Check:**
- Did you paste the correct Apollo URL?
- Is your Apify API token valid?
- Does the Apollo filter page exist?

### No leads in output
**Check:**
- Did all your leads get filtered as duplicates?
- Check each intermediate CSV to see where leads were removed
- Review the console output for filtering statistics

### Email verification fails
**Check:**
- Is your NeverBounce API key valid?
- Do you have credits in your NeverBounce account?
- Are there any emails in the input file?

### LinkedIn enrichment fails
**Check:**
- Is your BrightData token valid?
- Are the LinkedIn URLs formatted correctly?
- Do you have BrightData credits?

---

## Performance Tips

1. **Run in stages** - Don't run all 12 steps at once initially
2. **Test with small datasets** first
3. **Monitor API quotas** - OpenAI, NeverBounce, BrightData have rate limits
4. **Step 12 is slow** - LinkedIn enrichment can take hours for large datasets
5. **Check outputs** after each major step before continuing

---

## Example: Complete First Run

```bash
# 1. Test environment setup
python test_env_vars.py

# 2. Edit pipeline_importing.py
# Set: skip = [8,9,10,11,12]
# Set: input_builtwith_leads_file_path to your file

# 3. Run Steps 0-7
python pipeline_importing.py

# 4. Check outputs/verified_subsetted.csv exists

# 5. Edit pipeline_importing.py again
# Set: skip = [0,1,2,3,4,5,6,7]

# 6. Run Steps 8-12
python pipeline_importing.py

# 7. Check final output
# Open outputs/linkedin_enriched_leads.csv
```

---

## Quick Reference

**Run everything:**
```python
skip = []
```

**Run command:**
```bash
python pipeline_importing.py
```

**Test environment:**
```bash
python test_env_vars.py
```

**Check output:**
- Final file: `outputs/linkedin_enriched_leads.csv`
- Intermediate files: `outputs/` directory

---

**Need help?** Check PROJECT_DOCUMENTATION.md for detailed information about each step.
