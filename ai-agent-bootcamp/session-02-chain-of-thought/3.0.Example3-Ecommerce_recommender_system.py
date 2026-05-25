# pip install openai python-dotenv pandas
import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================= Load Data from CSV =================
user_profile = pd.read_csv("user_profile_ecommerce.csv").to_dict(orient="records")[0]
purchase_history = pd.read_csv("purchase_history.csv").to_dict(orient="records")
browsing_behavior = pd.read_csv("browsing_behavior.csv").to_dict(orient="records")
available_products = pd.read_csv("available_products.csv").to_dict(orient="records")

# Format product context (limit 20)
product_context = ""
for i, product in enumerate(available_products):
    product_context += f"Product {i+1}: {product['name']} - ${product['price']}\n"
    product_context += f"Category: {product['category']}, Brand: {product['brand']}\n"
    product_context += f"Description: {product['description'][:100]}...\n\n"

# ================= Recommendations Prompt =================
prompt_recommendations = f"""
Generate personalized product recommendations:

USER PROFILE:
{json.dumps(user_profile, indent=2)}

PURCHASE HISTORY:
{json.dumps(purchase_history, indent=2)}

BROWSING BEHAVIOR:
{json.dumps(browsing_behavior, indent=2)}

AVAILABLE PRODUCTS:
{product_context}

Steps:
1. Identify key preferences and interests from the user
2. Find purchase patterns that suggest product categories
3. Consider browsing for current interests
4. Match to available products
5. Rank recommendations

Provide top 5 product recommendations with detailed reasoning.
"""

response_recommendations = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_recommendations,
    temperature=0,
)

print("\nRECOMMENDATIONS:\n", response_recommendations.output_text)

# ================= Product Explanation Prompt =================
prompt_explanation = f"""
Generate a personalized explanation for why this product was recommended:

USER PROFILE:
{json.dumps(user_profile, indent=2)}

PRODUCT RECOMMENDATION:
Indoor Herb Garden Kit - A self-watering system to grow fresh herbs year-round in your kitchen.

Make the explanation:
1. Connect product features to user preferences
2. Reference relevant purchases or browsing
3. Show how it complements owned items
4. Explain why now is the right time
5. Add a personal touch
"""

response_explanation = client.responses.create(
    model="gpt-4o-mini",
    input=prompt_explanation,
    temperature=0,
)

print("\nPERSONALIZED PRODUCT EXPLANATION:\n", response_explanation.output_text)
