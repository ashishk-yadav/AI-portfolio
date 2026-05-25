# 📘 Modular Summarizer Demo — Practical Workshop Focus

## Overview
This project demonstrates a **Streamlit-based Document Summarizer** that compares multiple approaches to summarization using **OpenAI’s GPT-4o-mini** and **RAG (Retrieval-Augmented Generation)**.

Participants can upload large `.txt` or `.pdf` files, experiment with **four summarization strategies**, and evaluate their relative effectiveness.

The goal is to build practical intuition about **why RAG and advanced summarization workflows matter in real-world NLP applications**.

## Features
- 📂 **File Uploads**: Drag-and-drop TXT/PDF files for analysis.
- 🔍 **Baseline Summarization**: Direct summary of the full document.
- 🧠 **RAG Summarization**: Chunk, embed, and retrieve relevant context before summarizing (better for large/targeted queries).
- ⚙️ **Map-Reduce Summarization**: Summarize chunks individually (“map”), then merge them into a global summary (“reduce”).
- 🔗 **Chaining (Refinement)**: Iterative summarization where one summary is refined into a more structured one.
- 📊 **Evaluation Panel**: Rate clarity/accuracy of each summary (1–5). Ratings are saved for later analysis.

## Example Workflow
1. Upload a **50-page contract** in PDF format.  
2. Ask: *“Summarize key termination and liability clauses.”*  
   - **Baseline**: Attempts to summarize the whole document, but may miss specifics.  
   - **RAG**: Retrieves the exact clauses, producing a focused, accurate summary.  
   - **Map-Reduce**: Breaks down each section → merges into one cohesive view.  
   - **Chaining**: Takes a rough summary → polishes it into structured obligations/risks.  
3. Compare outputs, then rate them.

## Real-World Use Case Example
- **Legal Teams**: Upload a 100-page contract → instantly get obligations, risk factors, and key clauses.  
- **Finance Analysts**: Summarize covenants from a long loan agreement → highlight default triggers.  
- **Healthcare Providers**: Upload discharge summaries → extract patient follow-up plans and red flags.  
- **Policy Researchers**: Summarize large AI policy briefs → quickly understand recommendations and implications.  

This mirrors real-world scenarios where **time-constrained professionals need insights from massive documents quickly**.
