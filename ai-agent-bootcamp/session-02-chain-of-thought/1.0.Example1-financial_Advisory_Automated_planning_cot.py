import openai
import pandas as pd
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

# Read openai key from .env
load_dotenv()
open_ai_key = os.getenv("OPENAI_API_KEY")
openai.api_key = open_ai_key
# ----------------------------
# Step 1: Read data from CSV
# ----------------------------
# Example file: user_profile.csv
# age,income,savings,debt,dependents,risk_tolerance
# 42,120000,180000,220000,2,moderate

df = pd.read_csv("user_profile.csv")
row = df.iloc[0]   # take first row from CSV

user_profile = {
    "age": int(row["age"]),
    "income": int(row["income"]),
    "savings": int(row["savings"]),
    "debt": int(row["debt"]),
    "dependents": int(row["dependents"]),
    "risk_tolerance": row["risk_tolerance"]
}

investment_goals = """
I want to save for my children's college education (ages 8 and 10) 
while also growing my retirement fund. 
I can invest $1,500 monthly and prefer moderate risk.
"""

# ----------------------------
# Step 2: Connect to OpenAI
# ----------------------------
client = OpenAI(api_key=open_ai_key)

# ----------------------------
# Step 3: Generate a step by step Plan
# ----------------------------
plan_prompt = f"""
You are a financial planning assistant. 
A client has given you a profile and investment goals.

Your task: generate a list of step-by-step reasoning steps 
(like a numbered plan) to create an investment strategy.

CLIENT PROFILE:
{json.dumps(user_profile, indent=2)}

INVESTMENT GOALS:
{investment_goals}
"""

print("=========Planning Prompt======")
print(plan_prompt)

response = client.responses.create(
    model="gpt-4o-mini",
    input=plan_prompt,
    temperature=0
)

plan_text = response.output_text
steps = [step.strip() for step in plan_text.split("\n") if step.strip() and step[0].isdigit()]

print("\n--- Step 1: Generated Plan ---")
for step in steps:
    print(" -", step)

# ----------------------------
# Step 4: Execute Plan
# ----------------------------
results = []

print("\n--- Step 2: Step-by-Step Reasoning ---")
for step in steps:
    reasoning_prompt = f"""
    You are a financial advisor. Using the info below, 
    reason through this step.

    CLIENT PROFILE:
    {json.dumps(user_profile, indent=2)}

    INVESTMENT GOALS:
    {investment_goals}

    Step: {step}

    Thought:"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=reasoning_prompt,
        temperature=0
    )
    thought = response.output_text
    results.append((step, thought))

    print(f"\nStep: {step}\n{thought}")

# ----------------------------
# Step 5: Summarize Recommendation
# ----------------------------
compiled = "\n".join([f"{step}\n{thought}" for step, thought in results])

final_prompt = f"""
You are a financial planner. 
Summarize the findings and generate a final, 
personalized investment strategy based on this reasoning:

{compiled}

Final Answer:
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=final_prompt,
    temperature=0
)

final_advice = response.output_text

print("\n--- Step 3: Final Recommendation ---")
print(final_advice)

