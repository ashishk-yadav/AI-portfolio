import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read income, expenses, savings goal, and timeline from CSV
# Example structure of finance_info.csv:
# Type,Category,Amount
# Income,Salary,5800
# Expense,Housing,1800
# Expense,Utilities,350
# Expense,Groceries,600
# Expense,Transportation,400
# Expense,Entertainment,450
# Expense,Dining Out,500
# Expense,Shopping,600
# Expense,Subscriptions,120
# Expense,Miscellaneous,300
# Goal,Savings,12000
# Goal,Timeline,12

df = pd.read_csv("finance_info.csv")

income = df[df["Type"] == "Income"]["Amount"].sum()
expenses = df[df["Type"] == "Expense"].set_index("Category")["Amount"].to_dict()
savings_goal = df[(df["Type"] == "Goal") & (df["Category"] == "Savings")]["Amount"].iloc[0]
timeline_months = df[(df["Type"] == "Goal") & (df["Category"] == "Timeline")]["Amount"].iloc[0]

# Summarize expenses for readability
expenses_summary = "\n".join([f"- {cat}: ${amt}" for cat, amt in expenses.items()])

# --- Create Budget Plan ---

budget_prompt = f"""
Create a detailed budget plan based on the following information:

MONTHLY INCOME: ${income}

CURRENT EXPENSES:
{expenses_summary}

SAVINGS GOAL: ${savings_goal} in {timeline_months} months

Think through this step-by-step:
1. Calculate the monthly savings required to reach the goal
2. Analyze current spending patterns to identify areas for reduction
3. Create a recommended monthly budget with specific allocations
4. Suggest concrete actions to reduce expenses in key categories
5. Develop a contingency plan for unexpected expenses

Provide the complete budget plan with clear category allocations and actionable recommendations.
"""

budget_response = client.responses.create(
    model="gpt-4o-mini",
    input=budget_prompt,
    temperature=0,
)

budget_plan = budget_response.output_text
print("BUDGET PLAN:\n", budget_plan)

# --- Evaluate a Purchase ---
purchase_amount = 899
purchase_category = "Electronics"
purchase_description = "New smartphone to replace 3-year old device with cracked screen"

purchase_prompt = f"""
Evaluate if this purchase decision aligns with the user's budget plan:

PROPOSED PURCHASE:
- Amount: ${purchase_amount}
- Category: {purchase_category}
- Description: {purchase_description}

USER'S BUDGET CONTEXT:
- Monthly Income: ${income}
- Savings Goal: ${savings_goal} in {timeline_months} months

CURRENT BUDGET PLAN:
{budget_plan}

Think through this decision step-by-step:
1. Identify which budget category this purchase falls under
2. Determine if this purchase exceeds the allocated amount for that category
3. Assess the necessity and value of this purchase
4. Consider alternatives or postponement options
5. Provide a clear recommendation with justification

Should the user proceed with this purchase? Why or why not?
"""

purchase_response = client.responses.create(
    model="gpt-4o-mini",
    input=purchase_prompt,
    temperature=0,
)

print("\nPURCHASE EVALUATION:\n", purchase_response.output_text)
