import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Autogen Research Assistant", page_icon="📚")

from llm_provider import provider_sidebar

llm_cfg = provider_sidebar(key_prefix="research")

from agents import ResearchAgents
from data_loader import DataLoader

# Streamlit UI Title
st.title("📚 Virtual Research Assistant")

# Initialize AI Agents — provider is resolved from env vars set by provider_sidebar()
agents = ResearchAgents()

# Initialize DataLoader for fetching research papers
data_loader = DataLoader()

# Input field for the user to enter a research topic
query = st.text_input("Enter a research topic:")

# When the user clicks "Search"
if st.button("Search"):
    try:
        with st.spinner("Fetching papers from ArXiv…"):
            all_papers = data_loader.fetch_arxiv_papers(query)

        if not all_papers:
            st.warning("No papers found for that query. Try a different search term.")
        else:
            processed_papers = []
            with st.spinner(f"Summarising {len(all_papers)} paper(s) with {llm_cfg['provider']}…"):
                for paper in all_papers:
                    summary = agents.summarize_paper(paper["summary"])
                    adv_dis = agents.analyze_advantages_disadvantages(summary)
                    processed_papers.append({
                        "title": paper["title"],
                        "link": paper["link"],
                        "summary": summary,
                        "advantages_disadvantages": adv_dis,
                    })

            st.subheader("Top Research Papers:")
            for i, paper in enumerate(processed_papers, 1):
                st.markdown(f"### {i}. {paper['title']}")
                st.markdown(f"🔗 [Read Paper]({paper['link']})")
                st.write(f"**Summary:** {paper['summary']}")
                st.write(paper["advantages_disadvantages"])
                st.markdown("---")

    except RuntimeError as e:
        st.error(f"⚠️ {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")



