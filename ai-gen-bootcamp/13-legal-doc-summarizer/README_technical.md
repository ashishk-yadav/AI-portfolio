# Summarizer Demo — Technical Deep Dive

## Project Purpose
This demo is designed to **teach the evolution of summarization techniques** — from naive summarization to advanced **RAG and compositional pipelines**. Participants will not only use these features but also **look under the hood** at chunking, embeddings, retrieval, and model prompting.

## Architecture
1. **File Loader (`utils/io.py`)**  
   - Reads TXT/PDF into raw text.
2. **Chunking (`utils/chunking.py`)**  
   - Splits text into manageable windows (token-based).
3. **Embeddings (`utils/embeddings.py`)**  
   - Uses `text-embedding-3-small` to convert chunks into vectors.  
   - Enables semantic retrieval of relevant passages.
4. **Summarizers (`summarizers/`)**  
   - **Baseline**: Direct whole-document summarization.  
   - **RAG**: Retrieval-Augmented → query embeds → fetch top-k chunks → summarize.  
   - **Map-Reduce**: Parallel per-chunk summarization → merged summary.  
   - **Chaining**: Iterative refinement of summaries.  
5. **Evaluation (`evaluation/storage.py`)**  
   - Collects participant feedback into `ratings.csv`.

## Strengths of Each Method
- **Baseline**: Fast, but risks hallucinations/omissions on large docs.  
- **RAG**: Grounded in document text; reduces hallucination.  
- **Map-Reduce**: Scales well for *very large* files (e.g., >100 pages).  
- **Chaining**: Produces polished, structured, human-readable outputs.  

## Real-World Example: M&A Legal Due Diligence
Imagine a team of lawyers reviewing a **300-page merger agreement**.  
- **Baseline** → gives a generic summary, but too broad.  
- **RAG** → precisely extracts indemnity and liability clauses across sections.  
- **Map-Reduce** → breaks down annexures and schedules, then merges them into a cohesive report.  
- **Chaining** → converts the technical summary into an **executive brief for senior management**.

This setup mimics real workflows in consulting, law, and financial due diligence, showing participants the **practical business value** of these NLP techniques.
