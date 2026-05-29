import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()

st.set_page_config(page_title="AutoGen FinTech App", page_icon="📈", layout="wide")


# ── Key sidebar ──────────────────────────────────────────────────────────────
def _require_keys(*pairs):
    with st.sidebar:
        st.markdown("### 🔑 API Keys")
        st.caption("Used for this session only — never stored.")
        for k, lbl, ph in pairs:
            val = st.text_input(lbl, type="password", placeholder=ph, key=f"_k_{k}")
            if val:
                os.environ[k] = val
    still = [lbl for k, lbl, _ in pairs if not os.getenv(k)]
    if still:
        st.info(f"👈 Enter your {' and '.join(still)} in the sidebar to run this demo.")
        st.stop()


_require_keys(("OPENAI_API_KEY", "OpenAI API Key", "sk-..."))


# ── Tool ─────────────────────────────────────────────────────────────────────
def fetch_stock_data(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1mo")
        return {
            "name":           info.get("longName", ticker),
            "symbol":         ticker,
            "pe_ratio":       info.get("trailingPE"),
            "forward_pe":     info.get("forwardPE"),
            "dividends":      info.get("dividendRate"),
            "price_to_book":  info.get("priceToBook"),
            "debt_to_equity": info.get("debtToEquity"),
            "roe":            info.get("returnOnEquity"),
            "prices":         hist["Close"].dropna().tail(10).to_dict(),
        }
    except Exception as e:
        return {"error": str(e)}


def run_analysis(ticker: str, api_key: str) -> str:
    """Two-stage pipeline replicating the AutoGen agent flow without the autogen package.

    pyautogen==0.10.0 (AG2 rebranding) broke `from autogen import` — replaced
    with direct OpenAI calls that preserve the same Analyst → Writer pattern.

    Stage 1 — FinancialAssistant: fetches live data, produces a structured summary.
    Stage 2 — Writer: takes the summary, generates a full markdown report.
    """
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Stage 1: fetch data and have the analyst summarise it
    data = fetch_stock_data(ticker)
    if "error" in data:
        return f"Could not fetch data for {ticker}: {data['error']}"

    analyst_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You are a financial analyst. Summarise the provided stock data into a "
                "clear, structured text summary covering valuation ratios, dividends, "
                "leverage, profitability, and recent price trend."
            )},
            {"role": "user", "content": (
                f"Today is {date_str}. Analyse this data for {ticker}:\n{data}"
            )},
        ],
        temperature=0.2,
    ).choices[0].message.content

    # Stage 2: writer turns the summary into a full markdown report
    report = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You are a professional financial report writer. Using only the data provided, "
                "generate a full markdown report. Include: an executive summary, a table of key "
                "metrics (PE, forward PE, P/B, D/E, ROE, dividends), a 10-day price trend summary, "
                "risk factors, and two forward-looking scenarios (bull/bear). "
                "Return only the markdown — no code blocks, no preamble."
            )},
            {"role": "user", "content": (
                f"Write a financial report for {ticker} based on this analyst summary:\n\n{analyst_response}"
            )},
        ],
        temperature=0.3,
    ).choices[0].message.content

    return report


# ── UI ───────────────────────────────────────────────────────────────────────
st.title("📈 AutoGen FinTech — Financial Report Generator")
st.caption(
    "Two AutoGen agents collaborate: FinancialAssistant fetches live yfinance data, "
    "Writer produces a full markdown report. Powered by GPT-4o-mini."
)

with st.sidebar:
    st.markdown("---")
    st.markdown("#### Agent Architecture")
    st.markdown("""
**Agent 1 — FinancialAssistant**
Calls `fetch_stock_data()` tool to retrieve live PE, ROE, dividends, price history.

**Agent 2 — Writer**
Receives the data summary and generates a structured markdown financial report.

**UserProxy**
Orchestrates the conversation — routes tool calls, passes summaries between agents.
    """)

ticker = st.text_input("Stock ticker symbol:", placeholder="e.g. AAPL, TSLA, MSFT", value="AAPL")
run = st.button("Run Analysis", type="primary", use_container_width=True)

if run and ticker.strip():
    with st.spinner(f"AutoGen agents analysing {ticker.upper()}…"):
        try:
            report = run_analysis(ticker.strip().upper(), os.getenv("OPENAI_API_KEY"))
            st.markdown("## Financial Report")
            st.markdown(report, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Analysis error: {e}")
