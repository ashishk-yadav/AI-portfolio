import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Autogen Research Assistant", page_icon="📚")

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

_require_keys(("GROQ_API_KEY", "Groq API Key", "gsk_..."))

from agents import ResearchAgents
from data_loader import DataLoader

# Streamlit UI Title
st.title("📚 Virtual Research Assistant")

groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize AI Agents for summarization and analysis
agents = ResearchAgents(groq_api_key)

# Initialize DataLoader for fetching research papers
data_loader = DataLoader()

# Input field for the user to enter a research topic
query = st.text_input("Enter a research topic:")

# When the user clicks "Search"
if st.button("Search"):
    with st.spinner("Fetching research papers..."):  # Show a loading spinner
        
        # Fetch research papers from ArXiv and Google Scholar
        arxiv_papers = data_loader.fetch_arxiv_papers(query)
        # arxiv_papers = data_loader.fetch_google_scholar_papers(query)

        #google_scholar_papers = data_loader.fetch_google_scholar_papers(query)
        #all_papers = arxiv_papers + google_scholar_papers  # Combine results from both sources
        all_papers = arxiv_papers

        # If no papers are found, display an error message
        if not all_papers:
            st.error("Failed to fetch papers. Try again!")
        else:
            processed_papers = []

            # Process each paper: generate summary and analyze advantages/disadvantages
            for paper in all_papers:
                summary = agents.summarize_paper(paper['summary'])  # Generate summary
                adv_dis = agents.analyze_advantages_disadvantages(summary)  # Analyze pros/cons

                processed_papers.append({
                    "title": paper["title"],
                    "link": paper["link"],
                    "summary": summary,
                    "advantages_disadvantages": adv_dis,
                })

            # Display the processed research papers
            st.subheader("Top Research Papers:")
            for i, paper in enumerate(processed_papers, 1):
                st.markdown(f"### {i}. {paper['title']}")  # Paper title
                st.markdown(f"🔗 [Read Paper]({paper['link']})")  # Paper link
                st.write(f"**Summary:** {paper['summary']}")  # Paper summary
                st.write(f"{paper['advantages_disadvantages']}")  # Pros/cons analysis
                st.markdown("---")  # Separator between papers



