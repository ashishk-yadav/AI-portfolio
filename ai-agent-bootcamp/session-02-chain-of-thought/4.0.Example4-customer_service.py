import pandas as pd
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===============================
# Read data from CSVs
# ===============================
customer_data = pd.read_csv("customer_data.csv").to_dict(orient="records")[0]  # single customer
queries = pd.read_csv("customer_queries.csv").to_dict(orient="records")

conversation_history = []

# ===============================
# Process each customer query
# ===============================
for q in queries:
    query = q["query"]

    # ---- Intent Analysis ----
    prompt_intent = f"""
    Analyze the customer service query below to understand the customer's intent:

    CUSTOMER QUERY: "{query}"

    Think through this step-by-step:
    1. Identify the primary issue or request in the query
    2. Determine if this is a question, complaint, request for assistance, or feedback
    3. Identify any emotional tones (frustrated, confused, angry, satisfied)
    4. Extract key products, services, or account details mentioned
    5. Determine the priority level (low, medium, high)

    Provide your analysis in JSON format with these fields:
    - primary_intent
    - intent_type (question/complaint/request/feedback)
    - emotional_tone
    - mentioned_products
    - priority_level
    - key_details
    """

    resp_intent = client.responses.create(
        model="gpt-4o-mini",
        input=prompt_intent,
        temperature=0,
    )
    intent_analysis = resp_intent.output_text

    try:
        json_start = intent_analysis.find('{')
        json_end = intent_analysis.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            intent_json = json.loads(intent_analysis[json_start:json_end])
        else:
            intent_json = {"primary_intent": "unknown", "details": intent_analysis}
    except Exception as e:
        print(f"Warning: {e}")
        intent_json = {"primary_intent": "unknown", "details": intent_analysis}

    # ---- Response Plan ----
    history_str = "\n".join([f"{h['role']}: {h['content']}" for h in conversation_history[-6:]])
    context_str = json.dumps(customer_data, indent=2)

    prompt_plan = f"""
    Plan a response to this customer service interaction:

    INTENT ANALYSIS:
    {json.dumps(intent_json, indent=2)}

    CUSTOMER QUERY:
    "{query}"

    CUSTOMER CONTEXT:
    {context_str}

    CONVERSATION HISTORY:
    {history_str}

    Create a detailed plan for the response by:
    1. Determining what information is needed to address the query
    2. Identifying appropriate actions to resolve the issue
    3. Planning acknowledgment of customer emotions (especially if negative)
    4. Considering follow-up questions or options to present
    5. Structuring the response for clarity and empathy

    Provide your response plan in detail, outlining main points to address.
    """

    resp_plan = client.responses.create(
        model="gpt-4o-mini",
        input=prompt_plan,
        temperature=0,
    )
    response_plan = resp_plan.output_text

    # ---- Final Response ----
    prompt_response = f"""
    Based on this response plan, generate a compassionate, clear, and helpful customer service message:

    RESPONSE PLAN:
    {response_plan}

    Generate a natural-sounding customer service response that addresses all points in the plan
    while maintaining a supportive, professional tone. The response should be easy to understand
    and show genuine concern for the customer's needs.
    """

    resp_final = client.responses.create(
        model="gpt-4o-mini",
        input=prompt_response,
        temperature=0,
    )
    final_response = resp_final.output_text

    # ---- Save in conversation history ----
    conversation_history.append({"role": "customer", "content": query})
    conversation_history.append({"role": "agent", "content": final_response})

    # ---- Print Results ----
    print("\n==============================")
    print("CUSTOMER QUERY:", query)
    print("\nINTENT ANALYSIS:\n", json.dumps(intent_json, indent=2))
    print("\nRESPONSE PLAN:\n", response_plan)
    print("\nFINAL RESPONSE:\n", final_response)
