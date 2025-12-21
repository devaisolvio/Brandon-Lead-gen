import os
import pandas as pd

# 🔧 Step 1: Set your folder path
folder_path = 'inputs/'  # Replace this with your actual folder path

# 📦 Step 2: List to store DataFrames
all_dfs = []

# 🔁 Step 3: Loop through all CSV files in the folder
for filename in os.listdir(folder_path):
    do_not_include = ["Previous_Customers_and_Samples_Given.csv", "grouped_by_domain.csv"]
    if filename.endswith('.csv') and (filename not in do_not_include):
        file_path = os.path.join(folder_path, filename)
        # ⛔ Skip the first line of the file
        df = pd.read_csv(file_path, skiprows=1)
        df["tech"] = filename.split(".")[0]
        all_dfs.append(df)

# 🧩 Step 4: Combine all DataFrames
combined_df = pd.concat(all_dfs, ignore_index=True)

# 💾 Step 5: Save the result
combined_df.to_csv('combined_output.csv', index=False)

print("✅ Combined CSV created (first line of each file skipped): 'combined_output.csv'")

df = pd.read_csv('combined_output.csv')
print(df.head())

import pandas as pd

# Load the combined CSV
df = pd.read_csv('combined_output.csv')

# Group by 'Domain' and collect all 'tech' values into a list
grouped = df.groupby('Domain')['tech'].agg(list).reset_index()

# Optional: Remove duplicates in each list
grouped['tech'] = grouped['tech'].apply(lambda x: list(set(x)))

print(grouped.head(50))
# # Save to a new CSV if needed
grouped.to_csv('grouped_by_domain.csv', index=False)

# print("✅ Grouped by domain with tech values aggregated.")
