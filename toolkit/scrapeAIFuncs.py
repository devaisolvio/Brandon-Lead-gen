import pandas as pd
from toolkit.llmFuncs import llmCall
import time

def remove_non_ecommerce_companies(input_file_path, output_file_path):
    df = pd.read_csv(input_file_path)
    rows_to_keep = []
    for index, row in df.iterrows():
        org_short_desc = row["organization_short_description"]
        if(pd.isna(org_short_desc)):
            print("No short description")
            rows_to_keep.append(index)
        else:
            print(org_short_desc)

            # AI check
            prompt = '''Based on the short description of this company in [short description],
            is this an ecommerce company or D2C company? Return 1 if it is, 0 if it is not. Return only the number
            and nothing else.

            Be generous - err on the side of including more companies. But if it is obviously not ecommerce (i.e.
            selling a product online), return 0. For example if it sells services or consulting without
            any mention of physical products, return 0. As long as they mention selling something that could be a
            physical product, return 1.

            [short description]
            <<short description>>
            '''

            prompt = prompt.replace("<<short description>>", org_short_desc)
            llmOutput = llmCall(prompt)
            print(llmOutput)
            if(llmOutput == "1"):
                rows_to_keep.append(index)
            time.sleep(0.25)

    df = df.iloc[rows_to_keep]
    df.to_csv(output_file_path, index=False)

