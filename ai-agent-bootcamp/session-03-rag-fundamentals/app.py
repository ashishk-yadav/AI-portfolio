import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="RAG Fundamentals", page_icon="📚", layout="wide")


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
        st.info("Add your OpenAI API Key in the sidebar to run the RAG pipeline.\n\nGet one at [platform.openai.com](https://platform.openai.com).")
        st.stop()
    return os.getenv("OPENAI_API_KEY")


def build_rag(text: str, api_key: str):
    import chromadb
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_chroma import Chroma
    from langchain.schema import Document

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=c) for c in chunks]

    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    # EphemeralClient = in-memory, no SQLite tenant setup needed (fixes chromadb 0.5.x error)
    client = chromadb.EphemeralClient()
    vectorstore = Chroma.from_documents(docs, embeddings,
        collection_name="rag_demo", client=client)

    return vectorstore, chunks, ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0)


def query_rag(question: str, vectorstore, llm):
    from langchain.schema import HumanMessage
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    relevant_docs = retriever.get_relevant_documents(question)
    context = "\n\n---\n\n".join([d.page_content for d in relevant_docs])
    prompt = f"""Answer the question using ONLY the context below. If the answer is not in the context, say so.

Context:
{context}

Question: {question}"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content, relevant_docs


DEFAULT_DOC = """ACME Corp Employee Onboarding Guide

Welcome to ACME Corp. This guide covers your first 30 days.

Week 1 — Setup:
- Complete IT setup: laptop, email, Slack, VPN access (IT ticket required)
- Meet your manager for a 1:1 on Day 1 at 9 AM
- Review the company handbook at handbook.acmecorp.com
- HR will send your benefits enrollment link within 48 hours

Week 2 — Team Integration:
- Shadow at least two team members for a full day each
- Attend the weekly all-hands meeting every Tuesday at 10 AM EST
- Complete mandatory compliance training in the Learning Portal (due by Day 10)

Week 3 — First Contribution:
- Your manager will assign your first project by Day 15
- Set up 30-60-90 day goals with your manager using the OKR template
- Request access to production systems via the Security portal

Policies:
- Vacation: 15 days PTO per year, accrued monthly. Approval required 2 weeks in advance.
- Remote work: Up to 3 days per week with manager approval. Wednesdays are required in-office.
- Expense reimbursement: Submit within 30 days via Concur. Limit $75 per meal without pre-approval.
- Health benefits: Enroll within 30 days of start date or wait until open enrollment in November.

Contact:
- HR: hr@acmecorp.com | Benefits: benefits@acmecorp.com
- IT Helpdesk: Slack #it-help or ext. 4357
- Your buddy: assigned by HR within 48 hours of start
"""

st.title("📚 RAG Fundamentals — Build a Retrieval-Augmented Pipeline")
st.caption("Upload your own document or use the sample. Ask questions and watch each RAG stage: chunk → embed → retrieve → generate.")

api_key = get_openai_key()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("#### Document")
    doc_source = st.radio("Source", ["Use sample document", "Upload your own"], horizontal=True)

    if doc_source == "Upload your own":
        uploaded = st.file_uploader("Upload TXT or PDF", type=["txt", "pdf"])
        if uploaded:
            if uploaded.name.endswith(".pdf"):
                import pypdf
                reader = pypdf.PdfReader(uploaded)
                text = "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
            else:
                text = uploaded.read().decode("utf-8")
        else:
            text = None
    else:
        text = DEFAULT_DOC
        st.text_area("Sample document (ACME Onboarding Guide):", value=text, height=200, disabled=True)

    if text:
        st.markdown("#### Ask a Question")
        question = st.text_input("Question:", placeholder="What is the vacation policy?")

        if st.button("Run RAG Pipeline", type="primary", use_container_width=True):
            with st.spinner("Building index and retrieving…"):
                try:
                    vectorstore, chunks, llm = build_rag(text, api_key)
                    answer, docs = query_rag(question, vectorstore, llm)
                    st.session_state["rag_answer"] = answer
                    st.session_state["rag_chunks"] = [d.page_content for d in docs]
                    st.session_state["rag_total_chunks"] = len(chunks)
                except Exception as e:
                    st.error(f"Pipeline error: {e}")

with col2:
    st.markdown("#### Pipeline Output")
    if "rag_answer" in st.session_state:
        st.markdown("**Answer:**")
        st.success(st.session_state["rag_answer"])

        st.markdown(f"**Retrieved chunks** ({len(st.session_state['rag_chunks'])} of {st.session_state['rag_total_chunks']} total):")
        for i, chunk in enumerate(st.session_state["rag_chunks"], 1):
            with st.expander(f"Chunk {i}"):
                st.text(chunk)

        st.caption("Only these chunks were sent to the LLM — not the full document. This is why RAG is cost-efficient and precise.")
    else:
        st.info("Run the pipeline to see results here.")
        st.markdown("#### RAG Pipeline Stages")
        st.markdown("""
```
Document
   ↓ RecursiveCharacterTextSplitter (500 tokens, 50 overlap)
Chunks
   ↓ OpenAIEmbeddings (text-embedding-3-small)
Vectors → ChromaDB
   ↓ Similarity search (top-k=3)
Relevant chunks
   ↓ GPT-4o-mini with retrieved context
Answer + citations
```
        """)
