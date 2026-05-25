import pandas as pd
from openai import OpenAI
import json


import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read system and problem info from CSV
df = pd.read_csv("tech_support_info.csv")
product_type = df.loc[0, "product_type"]
problem_description = df.loc[0, "problem_description"]
system_specs = json.loads(df.loc[0, "system_specs"])

conversation_history = []
current_diagnosis = {}
troubleshooting_steps = ""

# Step 1: Diagnose Problem
specs_str = json.dumps(system_specs, indent=2) if system_specs else "Not provided"

prompt_diagnosis = f"""
As a technical support specialist, diagnose this customer's problem:

PRODUCT TYPE: {product_type}

PROBLEM DESCRIPTION: {problem_description}

SYSTEM SPECIFICATIONS:
{specs_str}

Think through this diagnosis step-by-step:
1. Identify the main symptoms described
2. Consider the most common causes of these symptoms for this product
3. Evaluate which potential causes best match the specific details provided
4. Assess the severity and urgency of the problem
5. Determine what additional information would help narrow down the cause

Provide your diagnosis in this format:
- Primary Issue: [Your assessment of the most likely problem]
- Potential Causes: [List of possible causes, from most to least likely]
- Severity: [Low/Medium/High]
- Additional Information Needed: [Questions to further narrow down the issue]
"""


response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_diagnosis,
    temperature=0,
)
diagnosis = response.output_text

conversation_history.append({"role": "agent", "content": diagnosis})
current_diagnosis = {"product_type": product_type, "problem_description": problem_description,
                     "system_specs": system_specs, "initial_diagnosis": diagnosis}

print("INITIAL DIAGNOSIS:\n", diagnosis)

# Step 2: Troubleshooting Plan
history_str = "\n".join([f"{entry['role']}: {entry['content']}" for entry in conversation_history])
prompt_plan = f"""
Based on this technical support conversation, create a step-by-step troubleshooting plan:

CONVERSATION HISTORY:
{history_str}

Create a detailed troubleshooting plan that:
1. Starts with simple, non-technical steps
2. Progresses to more advanced solutions
3. Includes clear instructions for each step
4. Explains what each step is attempting to resolve
5. Indicates when to proceed to the next step

Format the plan as a numbered list of steps, with clear instructions for each.
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_plan,
    temperature=0,
)
troubleshooting_steps = response.output_text
conversation_history.append({"role": "agent", "content": troubleshooting_steps})

print("\nTROUBLESHOOTING PLAN:\n", troubleshooting_steps)

# Step 3: Process troubleshooting results (Example: Step 1)
step_number = 1
result_description = """
I checked the running applications and found several programs running 
in the background. Closed them all, but battery still drained ~15% 
in 1 hour of light browsing.
"""
conversation_history.append({"role": "customer", "content": f"Result of Step {step_number}: {result_description}"})

history_str = "\n".join([f"{entry['role']}: {entry['content']}" for entry in conversation_history[-6:]])
prompt_result = f"""
The customer has completed troubleshooting step {step_number} with this result:

RESULT: {result_description}

RECENT CONVERSATION:
{history_str}

Based on this result, determine:
1. Was the step successful? (Yes/Partially/No)
2. What does this result tell us about the root cause?
3. Should the customer proceed, try another approach, or is issue resolved?
4. Provide next step guidance.
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_result,
    temperature=0,
)
next_steps = response.output_text
conversation_history.append({"role": "agent", "content": next_steps})

print("\nAFTER STEP 1:\n", next_steps)

# Step 4: Resolution Summary
history_str = "\n".join([f"{entry['role']}: {entry['content']}" for entry in conversation_history])
prompt_summary = f"""
Analyze this technical support conversation and create a comprehensive resolution summary:

CONVERSATION HISTORY:
{history_str}

Include:
1. Problem description
2. Diagnosed root cause
3. Key troubleshooting steps
4. Which step resolved it
5. Recommendations to prevent similar issues
6. Any follow-up needed
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_summary,
    temperature=0,
)
resolution_summary = response.output_text

print("\nRESOLUTION SUMMARY:\n", resolution_summary)
