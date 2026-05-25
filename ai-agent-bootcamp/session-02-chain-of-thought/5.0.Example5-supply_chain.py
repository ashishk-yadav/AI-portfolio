import pandas as pd
import json

from numpy.ma.core import outer
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load data from CSVs
product_data = pd.read_csv("product_data.csv").to_dict(orient="records")
sales_history = pd.read_csv("sales_history.csv").to_dict(orient="records")
supplier_info = pd.read_csv("supplier_info.csv").to_dict(orient="records")
warehouse_constraints = pd.read_csv("warehouse_constraints.csv").to_dict(orient="records")[0]  # single row

# -------------------------
# Step 1: Analyze Sales Patterns
# -------------------------
product_json = json.dumps(product_data[:5], indent=2) if len(product_data) > 5 else json.dumps(product_data, indent=2)
sales_json = json.dumps(sales_history[:10], indent=2) if len(sales_history) > 10 else json.dumps(sales_history, indent=2)

sales_prompt = f"""
Analyze these sales patterns to identify trends and make inventory forecasts:

PRODUCT DATA:
{product_json}
(Showing sample of {len(product_data)} products)

SALES HISTORY:
{sales_json}
(Showing sample of {len(sales_history)} records)

Perform a comprehensive analysis including:
1. Sales velocity and trends for each product category
2. Seasonality patterns and upcoming seasonal impacts
3. Identification of fast-moving vs. slow-moving products
4. Stockout incidents and their impact
5. Demand forecasting for the next 60 days

Provide actionable insights that can inform inventory optimization decisions.
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=sales_prompt,
    temperature=0
)

sales_analysis = response.output_text
# -------------------------
# Step 2: Evaluate Suppliers
# -------------------------
supplier_json = json.dumps(supplier_info[:5], indent=2) if len(supplier_info) > 5 else json.dumps(supplier_info, indent=2)

supplier_prompt = f"""
Evaluate these suppliers to inform procurement and inventory decisions:

SUPPLIER INFORMATION:
{supplier_json}
(Showing sample of {len(supplier_info)} suppliers)

Analyze the suppliers considering:
1. Reliability and on-time delivery performance
2. Lead times and variability
3. Cost structure and minimum order quantities
4. Quality consistency and defect rates
5. Geographic risks and transportation considerations

Provide insights on:
- Which suppliers are most reliable for different product categories
- Recommendations for supplier diversification or consolidation
- Strategies to mitigate risks from less reliable suppliers
- Opportunities to optimize ordering based on supplier terms
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=supplier_prompt,
    temperature=0
)

supplier_analysis = response.output_text

# -------------------------
# Step 3: Inventory Optimization
# -------------------------
inventory_prompt = f"""
Optimize inventory levels based on the following data:

SALES ANALYSIS:
{sales_analysis}

SUPPLIER ANALYSIS:
{supplier_analysis}

WAREHOUSE CONSTRAINTS:
{json.dumps(warehouse_constraints, indent=2)}

Think through this optimization problem step by step:
1. Identify products requiring immediate inventory adjustments
2. Calculate optimal reorder points considering sales velocity, supplier lead times, and safety stock
3. Determine economic order quantities that balance holding costs with ordering costs
4. Allocate limited warehouse space to maximize profitability and availability
5. Create a prioritized reordering schedule for the next 30 days

For each product category, provide specific, actionable recommendations including:
- Optimal inventory levels
- Reorder points and quantities
- Preferred suppliers
- Storage location strategies

Also identify any critical issues requiring immediate attention and any long-term strategic changes needed.
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=inventory_prompt,
    temperature=0
)

inventory_recommendations = response.output_text
# -------------------------
# Step 4: Procurement Plan
# -------------------------
budget_constraints = pd.read_csv("budget_constraints.csv").to_dict(orient="records")[0]  # single row
priority_products = pd.read_csv("priority_products.csv")["product_id"].tolist()  # list of priorities

procurement_prompt = f"""
Create a strategic procurement plan based on this inventory optimization analysis:

INVENTORY OPTIMIZATION RESULTS:
{inventory_recommendations}

BUDGET CONSTRAINTS:
{json.dumps(budget_constraints, indent=2)}

PRIORITY PRODUCTS:
{json.dumps(priority_products, indent=2)}

Develop a comprehensive procurement plan that:
1. Allocates the available budget across product categories optimally
2. Prioritizes critical inventory replenishments
3. Sequences purchases to maximize cash flow efficiency
4. Balances immediate needs with strategic long-term purchases
5. Includes contingency plans for supply disruptions

The plan should include:
- Specific purchase recommendations with quantities and timing
- Supplier selection rationale
- Budget allocation across categories
- Risk mitigation strategies
- Key performance indicators to track
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=procurement_prompt,
    temperature=0
)

procurement_plan = response.output_text
# -------------------------
# Print Results
# -------------------------
print("SALES ANALYSIS:\n", sales_analysis)
print("\nSUPPLIER ANALYSIS:\n", supplier_analysis)
print("\nINVENTORY RECOMMENDATIONS:\n", inventory_recommendations)
print("\nPROCUREMENT PLAN:\n", procurement_plan)
