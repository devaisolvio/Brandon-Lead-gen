import pandas as pd
from datetime import datetime, timedelta, timezone

#### Load in the leads from instantly - using file
df = pd.read_csv("outputs/instantly_leads.csv")
list_df = pd.read_csv("inputs/[Done]_All-Live-Intelligems-Sites.csv", skiprows=1)

print(df.head(), df.shape)
print(list_df.head(), list_df.shape)

# Convert 'timestamp_last_touch' column to datetime
df['timestamp_last_touch'] = pd.to_datetime(df['timestamp_last_touch'])

# Calculate the cutoff date (3 months = ~90 days ago from today)
cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)

# Subset rows where last touch was more than 90 days ago
df = df[df['timestamp_last_touch'] < cutoff_date]
print("meets cutoff", df.shape)
print(df.head())

# subset by rows that are in triple_whale_df
df = df[df['company_domain'].isin(list_df['Domain'])]
print(df.shape)
