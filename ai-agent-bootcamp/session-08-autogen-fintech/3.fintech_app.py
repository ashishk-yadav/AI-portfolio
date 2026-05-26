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
    """Build agents fresh for each run so the API key is always current."""
    from autogen import AssistantAgent, UserProxyAgent, register_function, initiate_chats

    llm_config = {"model": "gpt-4o-mini", "api_key": api_key}

    financial_assistant = AssistantAgent(
        name="FinancialAssistant",
        llm_config=llm_config,
    )
    writer = AssistantAgent(
        name="Writer",
        llm_config=llm_config,
        system_message=(
            "You are a professional financial report writer. Based only on the data provided, "
            "generate a full markdown-formatted report. Include: analysis, a data table of key metrics "
            "(PE, dividends, ROE, etc.), a summary of recent stock prices, and suggest future scenarios. "
            "Return only the markdown content, no explanations or code blocks."
        ),
    )
    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
    )
    register_function(
        fetch_stock_data,
        caller=financial_assistant,
        executor=user_proxy,
        name="fetch_stock_data",
        description="Fetch 1-month stock history and key ratios for a given ticker.",
    )

    date_str = datetime.now().strftime("%Y-%m-%d")
    financial_prompt = (
        f"Today is {date_str}. For ticker '{ticker}', call fetch_stock_data(ticker) once and collect the results. "
        "Return a JSON object summarising all data. Do not add ```json or ``` in the final output."
    )

    results = initiate_chats([{
        "sender": user_proxy,
        "recipient": financial_assistant,
        "message": financial_prompt,
        "summary_method": "reflection_with_llm",
        "summary_args": {"summary_prompt": "Summarise all financial data and return as a JSON object."},
    }])
    data_summary = results[0].summary

    report_results = initiate_chats([{
        "sender": user_proxy,
        "recipient": writer,
        "message": (
            f"Use the following financial data to generate the report:\n{data_summary}\n\n"
            "Generate a markdown financial report including tables, summaries, and future scenarios."
        ),
        "summary_method": "last_msg",
        "max_turns": 1,
    }])
    return report_results[-1].chat_history[-1]["content"]


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
