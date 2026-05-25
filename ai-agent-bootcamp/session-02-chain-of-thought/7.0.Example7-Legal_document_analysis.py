import csv
from openai import OpenAI
from datetime import datetime
import pandas as pd

import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========================
# INPUT CONTRACT
# ========================
contract_text = """
SERVICE AGREEMENT

This Service Agreement (the "Agreement") is entered into as of April 15, 2025 (the "Effective Date"), by and between:

ABC Tech Solutions, Inc., a Delaware corporation with its principal place of business at 123 Tech Lane, San Francisco, CA 94105 ("Service Provider"), and

XYZ Enterprises, LLC, a New York limited liability company with its principal place of business at 456 Business Ave, New York, NY 10001 ("Client").

WHEREAS, Service Provider is in the business of providing cybersecurity services and solutions;

WHEREAS, Client desires to engage Service Provider to provide certain cybersecurity services;

NOW, THEREFORE, in consideration of the mutual covenants and agreements hereinafter set forth, the parties agree as follows:

1. SERVICES
1.1 Service Provider shall provide to Client the cybersecurity services (collectively, the "Services") described in Exhibit A attached hereto.
1.2 Service Provider shall perform the Services in accordance with the terms and conditions of this Agreement and in compliance with all applicable laws and regulations.
1.3 Service Provider shall dedicate sufficient resources and qualified personnel to perform the Services.

2. COMPENSATION
2.1 Service Fees. Client shall pay Service Provider the fees set forth in Exhibit B attached hereto (the "Service Fees").
2.2 Expenses. Client shall reimburse Service Provider for all reasonable out-of-pocket expenses incurred in connection with the Services, provided that such expenses are approved in advance by Client.
2.3 Invoicing. Service Provider shall invoice Client monthly for Services performed and expenses incurred. Payment is due within thirty (30) days of receipt of invoice.
2.4 Late Payments. Any amount not paid when due shall bear interest at the rate of 1.5% per month or the maximum rate permitted by law, whichever is less.

3. TERM AND TERMINATION
3.1 Term. This Agreement shall commence on the Effective Date and continue for a period of two (2) years, unless earlier terminated as provided herein (the "Initial Term"). Thereafter, this Agreement shall automatically renew for successive one-year periods (each, a "Renewal Term"), unless either party provides written notice of non-renewal at least sixty (60) days prior to the end of the Initial Term or any Renewal Term.
3.2 Termination for Convenience. Client may terminate this Agreement for convenience upon ninety (90) days' written notice to Service Provider.
3.3 Termination for Cause. Either party may terminate this Agreement for cause if the other party materially breaches this Agreement and fails to cure such breach within thirty (30) days after receipt of written notice of such breach.

4. CONFIDENTIALITY
4.1 Definition. "Confidential Information" means all non-public information disclosed by one party (the "Disclosing Party") to the other party (the "Receiving Party"), whether orally or in writing, that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and the circumstances of disclosure.
"""

specific_concerns = [
    "Termination penalties",
    "Data ownership rights",
    "Service level guarantees",
    "Liability caps"
]

# ========================
# STEP 1: Identify Structure
# ========================
prompt_structure = f"""
Analyze this contract to identify its type and key structural elements.

First few paragraphs of the contract:
{contract_text[:3000]}...

Identify:
1. The type of contract (e.g., employment, lease, service agreement)
2. The parties involved
3. The main sections/components
4. Governing law jurisdiction

Provide this information in a structured format.
"""

response_structure = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_structure,
    temperature=0,
)

contract_structure = response_structure.output_text

# Save to CSV
with open("contract_structure.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["contract_structure"])
    writer.writerow([contract_structure])

# ========================
# STEP 2: Clause Analysis
# ========================
prompt_clauses = f"""
Perform a detailed analysis of the key clauses in this contract.

CONTRACT STRUCTURE:
{contract_structure}

CONTRACT TEXT:
{contract_text[:4000]}...

For each major clause, provide:
1. A plain language explanation of what it means
2. Which party benefits most from the clause
3. Potential risks or consequences
4. Industry standard comparison (if unusual or particularly one-sided)

Focus on:
- Payment and compensation terms
- Term and termination provisions
- Liability and indemnification
- Intellectual property rights
- Dispute resolution
- Any unusual or potentially problematic clauses

Structure your analysis by clause for clarity.
"""

response_clauses = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_clauses,
    temperature=0,
)

clause_analysis = response_clauses.output_text

# Save to CSV
with open("clause_analysis.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["clause_analysis"])
    writer.writerow([clause_analysis])

# ========================
# STEP 3: Overall Assessment
# ========================
concerns_str = ", ".join(specific_concerns) if specific_concerns else "general assessment"

prompt_assessment = f"""
Based on the detailed clause analysis, provide an overall assessment of this contract.

CLAUSE ANALYSIS:
{clause_analysis}

SPECIFIC CONCERNS TO ADDRESS:
{concerns_str}

Provide a comprehensive analysis that:
1. Summarizes the contract's purpose and structure
2. Highlights significant rights and obligations for each party
3. Identifies potential risks, ambiguities, or unfavorable terms
4. Explains implications of key clauses in plain language
5. Suggests potential negotiations or modifications

Structure your response with clear sections and conclude with actionable recommendations.
Include a disclaimer that this is informational and not legal advice.
"""

response_assessment = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_assessment,
    temperature=0,
)

overall_assessment = response_assessment.output_text

# Save to CSV
with open("overall_assessment.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["overall_assessment"])
    writer.writerow([overall_assessment])

# ========================
# STEP 4: Extract Obligations
# ========================
prompt_obligations = f"""
Based on this contract analysis, extract a structured list of obligations for each party:

CONTRACT ANALYSIS:
{overall_assessment}

For each party in the contract, list their:
1. Financial obligations
2. Performance/delivery obligations
3. Compliance requirements
4. Reporting/communication obligations
5. Key deadlines or timeframes

Format as a clear, actionable checklist for each party, organized by category.
"""

response_obligations = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_obligations,
    temperature=0,
)

obligations = response_obligations.output_text

# Save to CSV
with open("obligations.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["obligations"])
    writer.writerow([obligations])

# ========================
# PRINT RESULTS
# ========================
print("CONTRACT STRUCTURE:\n", contract_structure)
print("\nCLAUSE ANALYSIS:\n", clause_analysis)
print("\nOVERALL ASSESSMENT:\n", overall_assessment)
print("\nOBLIGATIONS CHECKLIST:\n", obligations)

# ========================
# DOWNLOAD LINKS (for Jupyter/Colab)
# ========================
# import shutil
#
# for filename in ["contract_structure.csv", "clause_analysis.csv", "overall_assessment.csv", "obligations.csv"]:
#     shutil.move(filename, f"{filename}")
#     print(f"Download {filename}: {filename}")
