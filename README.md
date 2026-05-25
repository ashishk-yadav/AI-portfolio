# Ashish Yadav — AI Portfolio
### Technical Product Manager | Enterprise AI & Platform Modernization

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Portfolio-orange?logo=github)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Enabled-1C3C3C?logo=langchain)

---

## About

With 19+ years leading platform-level initiatives across cloud infrastructure, data architecture, APIs, and AI in enterprise SaaS and healthcare IT, I have built a proven track record of translating complex technical constraints into clear product priorities. My work spans modernization roadmaps, AI-augmented capabilities, and compliance-aligned solutions for Fortune 500 clients including Aon, Eli Lilly, Rockwell Automation, John Hancock, and BMS. I hold PMP and CSM certifications and am a Google Cloud Generative AI Leader and Azure AI Fundamentals certified professional.

This portfolio represents my hands-on AI engineering journey — built deliberately to close the gap between business strategy and engineering execution. Rather than relying solely on theoretical knowledge, I enrolled in two structured bootcamps to build real, deployable AI systems from the ground up: the **AI Generative Bootcamp** (16 projects) and the **AI Agent Bootcamp** (8 sessions/projects), for a total of **24 end-to-end AI applications**.

Every project here is production-influenced — grounded in enterprise use cases across HealthTech, FinTech, Legal, and B2B SaaS domains. The goal is not to become a research ML engineer, but to be the TPM who can credibly architect AI solutions, evaluate build-vs-buy tradeoffs, write meaningful acceptance criteria, and partner with engineering teams on a technical level.

---

## Project Summary

| # | Project | Domain | Core Capability | Key Tech | Level |
|---|---------|--------|-----------------|----------|-------|
| 01 | Autogen Research Assistant | General AI | Multi-agent paper research across ArXiv/Scholar | AutoGen, Groq, Streamlit | Beginner |
| 02 | Multi-Agent Doctor Booking | HealthTech | Autonomous appointment scheduling via agent delegation | LangChain, Groq, FastAPI, Streamlit | Intermediate |
| 03 | AI Coding Agent | Enterprise/Dev Tools | RAG over codebase; explains, edits, runs code | LangChain, ChromaDB, OpenAI, Streamlit | Beginner |
| 04 | Customer Service Agent | Enterprise B2B | Context-aware support agent with embedded docs | LangChain, OpenAI, Streamlit | Intermediate |
| 05 | Product Sentiment Classifier | Enterprise B2B | Review ingestion, sentiment scoring, SQLite persistence | OpenAI Embeddings, SQLite, Streamlit | Intermediate |
| 06 | Resume & Cover Letter Generator | General AI | Personalized generation + GPT-4o-mini fine-tuning | OpenAI, Fine-tuning, Streamlit | Intermediate |
| 07 | Marketing Copy Generator | Enterprise B2B | A/B copy variants with style selector | OpenAI, Streamlit | Beginner |
| 08 | Fine-Tune TinyLlama (LoRA) | General AI / LLM | Domain adaptation via QLoRA on marketing/legal data | TinyLlama, LoRA, PEFT, transformers, bitsandbytes | Advanced |
| 09 | Image Captioning (CNN+LSTM) | General AI / CV | Caption generation combining CNN features + LSTM decoder | PyTorch, CNN, LSTM, Attention, BLIP | Advanced |
| 10 | Human Activity Recognition | HealthTech | Wearable sensor classification via LSTM | PyTorch LSTM, scikit-learn, Streamlit | Advanced |
| 11 | Chest X-Ray Disease Detection | HealthTech | Binary pneumonia classifier with Grad-CAM explainability | PyTorch, VGG-16, Grad-CAM, Streamlit | Advanced |
| 12 | Neural Style Transfer | General AI / CV | Artistic style transfer via VGG-19 optimization | PyTorch, VGG-19, NST, Streamlit | Intermediate |
| 13 | Legal Document Summarizer | Enterprise B2B | Multi-strategy RAG summarization (map-reduce, refine, RAG) | OpenAI, LangChain, RAG, Streamlit | Intermediate |
| 14 | News Topic Classifier | General AI | TF-IDF vs. Embeddings vs. LLM zero-shot comparison | OpenAI Embeddings, scikit-learn, Streamlit | Intermediate |
| 15 | Multilingual Chatbot | Enterprise B2B | Real-time translation + GPT chat in 50+ languages | OpenAI, deep-translator, Streamlit | Beginner |
| 16 | Document Q&A (RAG) | Enterprise B2B | End-to-end RAG over PDFs and text docs | LangChain, ChromaDB, OpenAI, Streamlit | Intermediate |
| S1 | LLM Setup & API Integration | General AI / Platform | OpenAI, Ollama, and HuggingFace model comparison | OpenAI, Ollama, HuggingFace, PyTorch | Beginner |
| S2 | Chain-of-Thought (10 Use Cases) | Enterprise / FinTech / HealthTech | CoT reasoning across 10 industry domains | OpenAI, Ollama, pandas | Intermediate |
| S3 | RAG Fundamentals | Enterprise B2B | Document chunking, embedding, and retrieval pipeline | LangChain, ChromaDB, OpenAI | Intermediate |
| S4 | Text-to-SQL | Enterprise B2B | Natural language to SQLite query conversion | OpenAI, SQLite, LangChain | Intermediate |
| S5 | Multi-Agent Orchestration | Enterprise / FinTech | QnA + data analyst + risk assessment agents | LangChain, OpenAI, Streamlit | Advanced |
| S6 | Browser Automation & Web Scraping | General AI / Platform | Selenium scraping + LangSmith observability | Selenium, BeautifulSoup, LangSmith, yfinance | Advanced |
| S7 | CrewAI Multi-Agent Systems | Enterprise B2B | Role-based agent teams for research, debate, support | CrewAI, OpenAI, LangChain | Advanced |
| S8 | AutoGen FinTech App | FinTech | Conversational financial analysis with AutoGen agents | AutoGen (AG2), OpenAI, yfinance, Streamlit | Advanced |

---

## Prerequisites & Setup

**Global requirements:**
- Python 3.10+
- API keys configured in `.env` (see `.env.example`)
- For GPU-accelerated projects (08, 09, 10, 11, 12): a CUDA-capable GPU is recommended; CPU fallback is available for all projects
- For local model projects (S1, S6, fine-tune): [Ollama](https://ollama.ai) installed with `gemma3:1b` pulled (`ollama pull gemma3:1b`)

**Quick start:**

```bash
git clone https://github.com/YOUR_USERNAME/ai-portfolio.git
cd ai-portfolio
cp .env.example .env
# Edit .env with your API keys

# To run any project:
cd ai-gen-bootcamp/01-autogen-research-agent
pip install -r requirements.txt
streamlit run app.py
```

Each project directory contains its own `README.md` with project-specific setup, architecture notes, and usage instructions.

---

## Repository Structure

```
ai-portfolio-repo/
├── README.md                          # This file
├── .gitignore                         # Python + AI/ML gitignore
├── .env.example                       # All API keys and config variables
├── docs/                              # GitHub Pages portfolio (ashishkyadav07.github.io/ai-portfolio)
├── ai-gen-bootcamp/                   # 16 projects — AI Generative Bootcamp
│   ├── 01-autogen-research-agent/
│   ├── 02-multi-agent-doctor-booking/
│   ├── 03-ai-coding-agent/
│   ├── 04-customer-service-agent/
│   ├── 05-product-sentiment-classifier/
│   ├── 06-resume-cover-letter-generator/
│   ├── 07-marketing-copy-generator/
│   ├── 08-finetune-tinyllama/
│   ├── 09-image-captioning-cnn-lstm/
│   ├── 10-human-activity-recognition/
│   ├── 11-chest-xray-detection/
│   ├── 12-neural-style-transfer/
│   ├── 13-legal-doc-summarizer/
│   ├── 14-news-topic-classifier/
│   ├── 15-multilingual-chatbot/
│   └── 16-document-qna-rag/
└── ai-agent-bootcamp/                 # 8 projects — AI Agent Bootcamp
    ├── session-01-llm-setup/
    ├── session-02-chain-of-thought/
    ├── session-03-rag-fundamentals/
    ├── session-04-text-to-sql/
    ├── session-05-multi-agent-orchestration/
    ├── session-06-browser-automation/
    ├── session-07-crewai-agents/
    └── session-08-autogen-fintech/
```

---

## Certifications & Background

| Certification | Issuer |
|---------------|--------|
| Project Management Professional (PMP) | PMI |
| Certified Scrum Master (CSM) | Scrum Alliance |
| Google Cloud Generative AI Leader | Google Cloud |
| Azure AI Fundamentals (AZ-900) | Microsoft |
| Azure AI Fundamentals (AI-900) | Microsoft |

---

## Contact

[GitHub](https://github.com/YOUR_USERNAME) | [LinkedIn](https://linkedin.com/in/ashishkyadav07) | ashishk.yadav@gmail.com

---

*Licensed under the [MIT License](LICENSE). Built with Python, LangChain, OpenAI, PyTorch, and a lot of late nights.*
