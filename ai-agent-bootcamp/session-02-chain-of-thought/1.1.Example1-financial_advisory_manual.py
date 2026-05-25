# pip install openai python-dotenv pandas

import os
import json
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# ----------------------------
# Step 1: Load API Key from .env
# ----------------------------
# .env file should contain:
# OPENAI_API_KEY=your_api_key_here
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env file.")

client = OpenAI(api_key=api_key)

# ----------------------------
# Step 2: Read User Profile from CSV
# ----------------------------
# Example CSV: user_profile.csv
# age,income,savings,debt,dependents,risk_tolerance
# 42,120000,180000,220000,2,moderate

df = pd.read_csv("user_profile.csv")
row = df.iloc[0]

user_profile = {
    "age": int(row["age"]),
    "income": int(row["income"]),
    "savings": int(row["savings"]),
    "debt": int(row["debt"]),
    "dependents": int(row["dependents"]),
    "risk_tolerance": row["risk_tolerance"]
}

# ----------------------------
# Step 3: Define Investment Goals
# ----------------------------
investment_goals = """
I want to save for my children's college education (ages 8 and 10) 
while also growing my retirement fund. 
I'm concerned about market volatility but want to balance growth with reasonable risk. 
I can invest $1,500 monthly.
"""

# ----------------------------
# Step 4: Create Prompt
# ----------------------------
prompt = f"""
As a financial advisor, provide investment recommendations for this client 
based only on the years 2020-2024:

CLIENT PROFILE:
{json.dumps(user_profile, indent=2)}

INVESTMENT GOALS:
{investment_goals}

Let's think through this step-by-step:
1. Analyze the client's risk tolerance based on age, financial situation, and goals
2. Consider current market conditions and economic factors
3. Evaluate appropriate asset allocation (stocks, bonds, alternatives)
4. Recommend specific investment vehicles and explain the rationale
5. Address potential concerns and provide risk mitigation strategies
"""

# ----------------------------
# Step 5: Call OpenAI
# ----------------------------
response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt,
    temperature=0
)

# ----------------------------
# Step 6: Print Advice
# ----------------------------
advice = response.output_text

print("\n--- FINAL INVESTMENT ADVICE ---")
print(advice)
