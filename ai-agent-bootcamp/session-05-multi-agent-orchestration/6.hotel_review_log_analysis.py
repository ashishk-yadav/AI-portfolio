import streamlit as st
import pandas as pd
import openai
# Set your API key here
import os

from dotenv import load_dotenv
load_dotenv()

LLM_MODEL = "gpt-4o-mini"  # or "gpt-4"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Replace this with your open ai key "SK-"


st.set_page_config(page_title="AI Review Improvement Dashboard", layout="wide")

st.title("Hospitality AI Agent – Self-Improving Review Analysis")

# Load data
import os
_log_path = "review_analysis_log.csv"
if os.path.exists(_log_path):
    df = pd.read_csv(_log_path)
else:
    df = pd.DataFrame()  # Empty dataframe as fallback

# Show iteration summary
st.write("### Iteration Log")
st.dataframe(df, use_container_width=True)

# Trend of improvements
st.write("### Top Issues and Suggestions Over Time")
selected_iter = st.slider("Select Iteration", 1, len(df), len(df))
selected_data = df[df["Iteration"] == selected_iter].iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top_Issues")
    st.success(selected_data["Top_Issues"])

with col2:
    st.subheader("Actionable Suggestions")
    st.info(selected_data["Suggestions"])

# Optional: Critique Evolution
st.write("### Critique Feedback")
st.text_area("Critique Notes", selected_data["Critique"], height=200)

