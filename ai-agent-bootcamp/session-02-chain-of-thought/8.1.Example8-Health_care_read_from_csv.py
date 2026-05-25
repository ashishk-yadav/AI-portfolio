import csv
import json
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================
# READ PATIENT DATA FROM CSV
# ============================
df = pd.read_csv("patient_info.csv")

# We'll just take the first row for now (extendable to loop later)
row = df.iloc[0]

patient_age = row["age"]
patient_gender = row["gender"]
symptoms = row["symptoms"]

try:
    medical_history = json.loads(row["medical_history"])
except Exception as e:
    print(f"Warning: {e}")
    medical_history = None

medical_history_str = json.dumps(medical_history, indent=2) if medical_history else "No significant medical history provided"

# ============================
# STEP 1: Symptom Analysis
# ============================
prompt_analysis = f"""
You are a medical reasoning assistant. Analyze these patient symptoms:

PATIENT:
- Age: {patient_age}
- Gender: {patient_gender}

REPORTED SYMPTOMS:
{symptoms}

MEDICAL HISTORY:
{medical_history_str}

Think through this systematically:
1. Identify and categorize the primary symptoms
2. Consider how the symptoms might relate to each other
3. List possible causes from most to least likely, given the patient profile
4. Identify red flags or warning signs that require urgent attention
5. Suggest appropriate next steps (e.g., home care, specialist consultation, emergency care)

NOTE: Include a prominent disclaimer that this is not a diagnosis and the patient should 
consult a licensed healthcare provider for proper medical advice.
"""

response_analysis = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_analysis,
    temperature=0,
)

analysis = response_analysis.output_text

# Save to CSV
with open("symptom_analysis.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["symptom_analysis"])
    writer.writerow([analysis])

print("SYMPTOM ANALYSIS:\n", analysis)

# ============================
# STEP 2: Diagnostic Path
# ============================
additional_info = "Patient also mentions that the headaches sometimes wake her at night, and she's noticed increased urination frequency."

prompt_diagnostic = f"""
Based on the initial symptom analysis, recommend a structured diagnostic path:

INITIAL ANALYSIS:
{analysis}

ADDITIONAL INFORMATION:
{additional_info}

Provide a step-by-step recommended diagnostic approach:
1. What immediate tests or examinations would be most informative?
2. Which specialists might need to be consulted?
3. What further information would help narrow the diagnostic possibilities?
4. Are there any lifestyle modifications that might help while seeking diagnosis?
5. What signs would indicate a need to escalate care?

Include a clear disclaimer about the recommendations being informational only and 
the importance of consulting healthcare professionals.
"""

response_diagnostic = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_diagnostic,
    temperature=0,
)

diagnostic_path = response_diagnostic.output_text

# Save to CSV
with open("diagnostic_path.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["diagnostic_path"])
    writer.writerow([diagnostic_path])

print("\nRECOMMENDED DIAGNOSTIC PATH:\n", diagnostic_path)

