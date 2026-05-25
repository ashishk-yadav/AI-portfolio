import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Multi-Agent Doctor Booking", page_icon="🩺", layout="centered")


# ── Key sidebar — must come before any LLM imports ──────────────────────────
def _require_keys(*pairs):
    needed = [(k, lbl, ph) for k, lbl, ph in pairs if not os.getenv(k)]
    if not needed:
        return
    with st.sidebar:
        st.markdown("### 🔑 API Keys")
        st.caption("Used for this session only — never stored.")
        for k, lbl, ph in needed:
            val = st.text_input(lbl, type="password", placeholder=ph, key=f"_k_{k}")
            if val:
                os.environ[k] = val
    still = [lbl for k, lbl, _ in pairs if not os.getenv(k)]
    if still:
        st.info(f"👈 Enter your {' and '.join(still)} in the sidebar to run this demo.")
        st.stop()


_require_keys(
    ("GROQ_API_KEY", "Groq API Key", "gsk_..."),
)

# ── LLM imports (safe — key is set above) ───────────────────────────────────
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage


# ── Agents ──────────────────────────────────────────────────────────────────
def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
    )


def intake_agent(patient_id: str, query: str, llm) -> str:
    messages = [
        SystemMessage(content=(
            "You are a patient intake agent for a medical clinic. "
            "Extract: the type of appointment needed, preferred date/time, urgency level, and any relevant symptoms. "
            "Respond in a structured format."
        )),
        HumanMessage(content=f"Patient ID: {patient_id}\nRequest: {query}"),
    ]
    return llm.invoke(messages).content


def availability_agent(intake_summary: str, llm) -> str:
    messages = [
        SystemMessage(content=(
            "You are a clinic scheduling agent. Based on the intake summary, "
            "simulate checking available slots and provide 2-3 concrete appointment options "
            "with date, time, doctor name, and department. Be realistic."
        )),
        HumanMessage(content=f"Intake summary:\n{intake_summary}"),
    ]
    return llm.invoke(messages).content


def confirmation_agent(patient_id: str, selected_slot: str, intake_summary: str, llm) -> str:
    messages = [
        SystemMessage(content=(
            "You are a booking confirmation agent. Generate a professional appointment confirmation "
            "message including: appointment details, what to bring, cancellation policy (24h notice), "
            "and a reminder that this is a demo system."
        )),
        HumanMessage(content=(
            f"Patient ID: {patient_id}\n"
            f"Selected slot: {selected_slot}\n"
            f"Reason for visit: {intake_summary[:200]}"
        )),
    ]
    return llm.invoke(messages).content


# ── UI ───────────────────────────────────────────────────────────────────────
st.title("🩺 Multi-Agent Doctor Booking System")
st.caption(
    "Three-agent LangChain pipeline — intake → availability → confirmation. "
    "Powered by Groq (Llama 3.1)."
)

with st.sidebar:
    st.markdown("---")
    st.markdown("#### Agent Architecture")
    st.markdown("""
**Agent 1 — Intake**
Extracts appointment type, urgency, and symptoms from patient request.

**Agent 2 — Availability**
Checks calendar and returns available slots matching the request.

**Agent 3 — Confirmation**
Generates a formal booking confirmation with all details.
    """)

patient_id = st.text_input("Patient ID", placeholder="e.g., P-1042", value="P-1042")
query = st.text_area(
    "Describe your appointment need:",
    value="I need to see a dentist as soon as possible. I have a severe toothache and some swelling.",
    height=100,
)

if "booking_state" not in st.session_state:
    st.session_state.booking_state = None

if st.button("Start Booking", type="primary", use_container_width=True):
    llm = get_llm()
    with st.spinner("Agent 1 — Processing intake…"):
        intake = intake_agent(patient_id, query, llm)
    with st.spinner("Agent 2 — Checking availability…"):
        slots = availability_agent(intake, llm)
    st.session_state.booking_state = {"intake": intake, "slots": slots, "confirmed": False}

if st.session_state.booking_state and not st.session_state.booking_state.get("confirmed"):
    state = st.session_state.booking_state

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Agent 1 — Intake Summary")
        st.info(state["intake"])
    with col2:
        st.markdown("#### Agent 2 — Available Slots")
        st.success(state["slots"])

    selected = st.text_input("Which slot would you like to book?", placeholder="e.g., Tuesday May 28 at 2:30 PM with Dr. Chen")
    if st.button("Confirm Booking", type="primary") and selected:
        llm = get_llm()
        with st.spinner("Agent 3 — Generating confirmation…"):
            confirmation = confirmation_agent(patient_id, selected, state["intake"], llm)
        st.session_state.booking_state["confirmation"] = confirmation
        st.session_state.booking_state["confirmed"] = True
        st.rerun()

if st.session_state.booking_state and st.session_state.booking_state.get("confirmed"):
    st.markdown("#### Agent 3 — Booking Confirmation")
    st.success(st.session_state.booking_state["confirmation"])
    if st.button("Start New Booking"):
        st.session_state.booking_state = None
        st.rerun()
