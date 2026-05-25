import csv
import json
from openai import OpenAI


import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================
# INPUT DATA
# ============================
symptoms = """
- Persistent headache for the past 3 weeks, typically worse in the morning
- Occasional dizziness when standing up quickly
- Blurred vision in right eye
- Fatigue that doesn't improve with rest
- Lost 5 pounds in the last month without trying
"""

medical_history = {
    "chronic_conditions": ["Hypertension (diagnosed 5 years ago)"],
    "medications": ["Lisinopril 10mg daily"],
    "allergies": ["Penicillin"],
    "family_history": ["Father had stroke at 65", "Mother with type 2 diabetes"],
    "surgeries": ["Appendectomy (15 years ago)"],
    "social_history": {
        "smoking": "Never",
        "alcohol": "Occasional (1-2 drinks/week)",
        "exercise": "Minimal"
    }
}

medical_history_str = json.dumps(medical_history, indent=2) if medical_history else "No significant medical history provided"

# ============================
# STEP 1: Symptom Analysis
# ============================
prompt_analysis = f"""
You are a medical reasoning assistant. Analyze these patient symptoms:

PATIENT:
- Age: 58
- Gender: Female

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
#
# # ============================
# # DOWNLOAD LINKS (if in Jupyter/Colab)
# # ============================
# import shutil
# for filename in ["symptom_analysis.csv", "diagnostic_path.csv"]:
#     shutil.move(filename, f"/mnt/data/{filename}")
#     print(f"Download {filename}: /mnt/data/{filename}")
