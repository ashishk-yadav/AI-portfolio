# pip install openai python-dotenv pandas

import os
import json
from datetime import datetime, timedelta
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
# Step 2: Read User History from CSV
# ----------------------------
# Example file: user_history.csv
# timestamp,amount,merchant,merchant_category,location
# 2025-04-18T10:30:00,42.15,Starbucks,Food,New York
# 2025-04-17T18:20:00,125.30,Whole Foods,Grocery,New York
# 2025-04-15T12:10:00,85.00,Amazon,Retail,Online
# 2025-04-12T09:15:00,35.50,Starbucks,Food,New York
# 2025-04-10T20:20:00,200.00,Nike,Retail,New York

df = pd.read_csv("user_history.csv")
user_history = df.to_dict(orient="records")

# ----------------------------
# Step 3: Suspicious Transaction (hardcoded here but in real world it will come when a user os swiping their card)
# ----------------------------
suspicious_transaction = {
    "timestamp": "2025-04-19T03:45:00",
    "amount": 9999.99,
    "merchant": "Electronics Store",
    "merchant_category": "Electronics",
    "location": "New Delhi"
}

# ----------------------------
# Step 4: Extract Features
# ----------------------------
amounts = [tx["amount"] for tx in user_history]
avg_amount = sum(amounts) / len(amounts) if amounts else 0

locations = [tx["location"] for tx in user_history]
common_locations = set([loc for loc in locations if locations.count(loc) > 1])

recent_count = 0
if user_history:
    current_time = datetime.fromisoformat(suspicious_transaction["timestamp"])
    for tx in user_history:
        tx_time = datetime.fromisoformat(tx["timestamp"])
        if current_time - tx_time <= timedelta(hours=24):
            recent_count += 1

features = {
    "avg_transaction_amount": avg_amount,
    "transaction_velocity_24h": recent_count,
    "common_locations": list(common_locations),
    "usual_merchant_categories": list(set([tx["merchant_category"] for tx in user_history])),
    "transaction_count_30d": len(user_history),
    "highest_single_amount": max(amounts) if amounts else 0,
}

# ----------------------------
# Step 5: Prompt GPT for Fraud Analysis. The step by step plan is given by Subject Matter expertise
# ----------------------------
prompt = f"""
Analyze this financial transaction for potential fraud:

CURRENT TRANSACTION:
{json.dumps(suspicious_transaction, indent=2)}

USER HISTORY SUMMARY:
{json.dumps(features, indent=2)}

Think step-by-step to determine if this transaction is fraudulent:
1. Analyze location patterns and whether the current transaction location is suspicious
2. Evaluate transaction amount in relation to user's typical spending
3. Consider the merchant category and if it aligns with user's normal habits
4. Assess transaction timing and frequency compared to patterns
5. Identify specific fraud indicators present in this transaction
6. Provide a fraud risk score (0-100) with explanation in a JSON format

Give more weight to location consistency.
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt,
    temperature=0
)

# ----------------------------
# Step 6: Print Result
# ----------------------------
analysis = response.output_text

print("\n--- Fraud Analysis ---")
print(analysis)
