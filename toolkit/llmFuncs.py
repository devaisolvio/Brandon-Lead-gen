from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def llmCall(prompt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Make a chat completion request
    response = client.chat.completions.create(
        model="gpt-4.1",  # or "gpt-3.5-turbo"
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )

    # 3. Print the result
    return response.choices[0].message.content

