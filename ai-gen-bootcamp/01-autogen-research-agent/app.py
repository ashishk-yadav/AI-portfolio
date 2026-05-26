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



