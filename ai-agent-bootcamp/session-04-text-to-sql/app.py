import os
import sqlite3
import json
import re
import tempfile
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Text-to-SQL", page_icon="🗄️", layout="wide")


def get_openai_key():
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    with st.sidebar:
        st.markdown("### 🔑 API Keys")
        st.caption("Used for this session only — never stored.")
        val = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        if val:
            os.environ["OPENAI_API_KEY"] = val
    if not os.getenv("OPENAI_API_KEY"):
        st.info("Add your OpenAI API Key in the sidebar to run Text-to-SQL.\n\nGet one at [platform.openai.com](https://platform.openai.com).")
        st.stop()
    return os.getenv("OPENAI_API_KEY")


def build_db(path: str):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY, name TEXT, email TEXT,
    signup_date DATE, plan TEXT, mrr REAL
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, customer_id INTEGER, product TEXT,
    amount REAL, order_date DATE, status TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, stock INTEGER
);
    """)
    cur.execute("SELECT COUNT(*) FROM customers")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?)", [
            (1, "Alice Johnson",  "alice@example.com",  "2024-01-15", "Enterprise", 2400),
            (2, "Bob Smith",      "bob@example.com",    "2024-03-01", "Pro",         490),
            (3, "Clara White",    "clara@example.com",  "2024-06-10", "Starter",      99),
            (4, "David Lee",      "david@example.com",  "2025-01-20", "Enterprise",  2400),
            (5, "Emma Torres",    "emma@example.com",   "2025-02-14", "Pro",          490),
        ])
        cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", [
            (1, 1, "Platform License",  2400, "2024-01-15", "paid"),
            (2, 2, "Pro Subscription",   490, "2024-03-01", "paid"),
            (3, 1, "Add-on: Analytics",  800, "2024-07-01", "paid"),
            (4, 3, "Starter Plan",        99, "2024-06-10", "paid"),
            (5, 4, "Platform License",  2400, "2025-01-20", "paid"),
            (6, 5, "Pro Subscription",   490, "2025-02-14", "pending"),
        ])
        cur.executemany("INSERT INTO products VALUES (?,?,?,?,?)", [
            (1, "Platform License", "Core",      2400, 999),
            (2, "Pro Subscription", "Core",       490, 999),
            (3, "Starter Plan",     "Core",        99, 999),
            (4, "Add-on: Analytics","Add-on",     800,  50),
            (5, "Add-on: API",      "Add-on",     600,  50),
        ])
    conn.commit()
    return conn


SCHEMA = """
Table: customers  — id, name, email, signup_date, plan (Starter/Pro/Enterprise), mrr (monthly recurring revenue)
Table: orders     — id, customer_id, product, amount, order_date, status (paid/pending)
Table: products   — id, name, category (Core/Add-on), price, stock
"""

SAMPLE_QUESTIONS = [
    "Show all Enterprise customers",
    "What is the total MRR?",
    "Which customers signed up in 2025?",
    "List all paid orders with their customer names",
    "What is the average order amount by product?",
    "Show customers who have placed more than one order",
]


def generate_sql(question: str, api_key: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    prompt = f"""You are an expert SQL writer for SQLite. Given the schema below, write a SQL query that answers the question.
Return ONLY valid SQL — no markdown, no explanation.

Schema:
{SCHEMA}

Question: {question}

SQL:"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0,
    )
    sql = response.choices[0].message.content.strip()
    sql = re.sub(r"```(?:sql)?", "", sql).strip().rstrip("`").strip()
    return sql


st.title("🗄️ Text-to-SQL — Natural Language Database Queries")
st.caption("Type a plain-English question. GPT-4o-mini generates the SQL, runs it against a live SQLite DB, and returns results.")

api_key = get_openai_key()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("#### Database Schema")
    st.code(SCHEMA.strip(), language="text")

    st.markdown("#### Sample Questions")
    selected = st.selectbox("Pick a sample or write your own below:", ["— write your own —"] + SAMPLE_QUESTIONS)
    default_q = "" if selected == "— write your own —" else selected
    question = st.text_input("Your question:", value=default_q, placeholder="e.g. Show all customers on the Pro plan")

    if st.button("Generate & Run SQL", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            with st.spinner("Generating SQL and querying database…"):
                try:
                    sql = generate_sql(question, api_key)
                    st.session_state["sql"] = sql
                    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
                        db_path = f.name
                    conn = build_db(db_path)
                    cur = conn.cursor()
                    cur.execute(sql)
                    rows = cur.fetchall()
                    cols = [d[0] for d in cur.description] if cur.description else []
                    conn.close()
                    st.session_state["results"] = (cols, rows)
                    st.session_state["error"] = None
                except Exception as e:
                    st.session_state["error"] = str(e)
                    st.session_state["results"] = None

with col2:
    st.markdown("#### Generated SQL")
    if "sql" in st.session_state and st.session_state["sql"]:
        st.code(st.session_state["sql"], language="sql")
    else:
        st.info("SQL will appear here after you submit a question.")

    st.markdown("#### Query Results")
    if "error" in st.session_state and st.session_state.get("error"):
        st.error(f"SQL error: {st.session_state['error']}")
    elif "results" in st.session_state and st.session_state["results"]:
        cols, rows = st.session_state["results"]
        if rows:
            import pandas as pd
            df = pd.DataFrame(rows, columns=cols)
            st.dataframe(df, use_container_width=True)
            st.caption(f"{len(rows)} row(s) returned")
        else:
            st.info("Query returned no results.")
    else:
        st.info("Results will appear here.")
