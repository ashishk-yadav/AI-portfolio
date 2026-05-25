# pip install python-dotenv openai

# Import packages

import os
from dotenv import load_dotenv
from openai import OpenAI

#  Load .env from your working directory (or give an explicit path)
load_dotenv()
# Get openai key from environment file
openai_key = os.getenv("OPENAI_API_KEY")

# Task Description
task = """Write a 50 word summary on ethics in AI."""

# Initialize openai
client = OpenAI(api_key=openai_key)

# Call GPT-4o-mini model
response = client.responses.create(
    model="gpt-4o-mini", # Name of the openai model
    input=task # Instruction or prompt which will be passed to GPT model
)

# Read the response
print(response.output_text)
