import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="CrewAI Multi-Agent — EdTech", page_icon="🎓", layout="wide")


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

# ── CrewAI imports (safe — key is set above) ─────────────────────────────────
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI


# ── Agents ───────────────────────────────────────────────────────────────────
def build_crew(api_key: str):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, api_key=api_key)

    student_support = Agent(
        role="Student Support Assistant",
        goal="Help students with academic or platform-related concerns",
        backstory="Handles student inquiries about the EdTech platform, course access, deadlines, or grading.",
        llm=llm,
        verbose=False,
    )
    content_guide = Agent(
        role="Educational Content Guide",
        goal="Provide relevant and engaging learning resources for students",
        backstory="An AI trained on curriculum and learning methods to suggest helpful content based on student needs.",
        llm=llm,
        verbose=False,
    )
    feedback_analyst = Agent(
        role="Feedback Classifier",
        goal="Extract and classify sentiment and feedback from student messages",
        backstory="Helps product and content teams understand how students feel and what they want improved.",
        llm=llm,
        verbose=False,
    )
    return student_support, content_guide, feedback_analyst


def run_crew(student_message: str, api_key: str) -> dict:
    student_support, content_guide, feedback_analyst = build_crew(api_key)

    support_task = Task(
        description=f"Respond to the student's question or concern: '{student_message}'. Be empathetic, informative, and friendly.",
        expected_output="A clear and kind support message addressing the student's need.",
        agent=student_support,
    )
    content_task = Task(
        description=f"Based on this message: '{student_message}', suggest relevant study materials (e.g., videos, articles, practice).",
        expected_output="At least one high-quality resource recommendation tailored to the topic.",
        agent=content_guide,
    )
    feedback_task = Task(
        description=f"Extract feedback from the message: '{student_message}' and classify it (Praise / Complaint / Feature Request / Confusion / N/A).",
        expected_output="Feedback category and a short summary.",
        agent=feedback_analyst,
    )

    crew = Crew(
        agents=[student_support, content_guide, feedback_analyst],
        tasks=[support_task, content_task, feedback_task],
        verbose=False,
    )
    result = crew.kickoff(inputs={"student_message": student_message})

    outputs = {}
    for task in [support_task, content_task, feedback_task]:
        outputs[task.agent.role] = task.output.raw if task.output else ""
    return outputs


# ── UI ───────────────────────────────────────────────────────────────────────
st.title("🎓 CrewAI Multi-Agent EdTech System")
st.caption(
    "Three specialized CrewAI agents handle student support, content recommendations, "
    "and feedback classification — in parallel, from a single student message."
)

with st.sidebar:
    st.markdown("---")
    st.markdown("#### Crew Architecture")
    st.markdown("""
**Agent 1 — Student Support**
Empathetic response to the student's concern or question.

**Agent 2 — Content Guide**
Recommends study materials, videos, or practice resources.

**Agent 3 — Feedback Classifier**
Tags the message: Praise / Complaint / Feature Request / Confusion.
    """)
    st.markdown("#### Why CrewAI?")
    st.markdown(
        "Role-based agents handle distinct tasks independently and in sequence, "
        "mimicking how a real EdTech support team would triage a student request."
    )

SAMPLES = [
    "I'm struggling with calculus integrals and I wish there were more interactive examples. Also, the quiz timer is too short.",
    "The video lectures are amazing! But I can't access the Week 3 assignment — it says 'locked' even though I completed Week 2.",
    "Can you explain the difference between supervised and unsupervised learning? I keep getting confused.",
    "I got a bad grade on my last quiz but the feedback was empty. I don't know what I did wrong.",
]

sample = st.selectbox("Choose a sample message or write your own:", ["— write your own —"] + SAMPLES)
message = st.text_area(
    "Student message:",
    value="" if sample == "— write your own —" else sample,
    height=120,
    placeholder="Type a student question, concern, or feedback…",
)

if st.button("Run Crew", type="primary", use_container_width=True):
    if not message.strip():
        st.warning("Enter a student message first.")
    else:
        with st.spinner("Running 3 CrewAI agents…"):
            try:
                outputs = run_crew(message, os.getenv("OPENAI_API_KEY"))
                st.session_state["crew_outputs"] = outputs
            except Exception as e:
                st.error(f"Crew error: {e}")

if "crew_outputs" in st.session_state and st.session_state["crew_outputs"]:
    outputs = st.session_state["crew_outputs"]
    col1, col2, col3 = st.columns(3)
    labels = {
        "Student Support Assistant": ("💬 Support Response", col1),
        "Educational Content Guide": ("📚 Content Recommendation", col2),
        "Feedback Classifier": ("🏷️ Feedback Classification", col3),
    }
    for role, (title, col) in labels.items():
        with col:
            st.markdown(f"#### {title}")
            st.info(outputs.get(role, "No output."))
