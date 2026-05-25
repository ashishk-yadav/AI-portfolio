# CLAUDE.md — AI Portfolio Context

This file gives Claude Code full context on this project. Read it before doing anything.

---

## What This Repo Is

A production-ready GitHub portfolio for **Ashish Yadav**, Technical Product Manager (19+ years, enterprise SaaS + healthcare IT). Contains 24 AI bootcamp projects cleaned up, hardened, documented, and ready for client demos.

- **Target role:** Technical Product Manager
- **Demo audience:** Potential clients (enterprise B2B, HealthTech, FinTech)
- **GitHub Pages:** `docs/index.html` — deploy via Settings → Pages → Source: `docs/`

---

## Repo Structure

```
ai-portfolio-repo/
├── README.md              # Root — 24-project table, Ashish's bio, global setup
├── .gitignore             # Python, ML weights, .env, datasets, runtime artefacts
├── .env.example           # Global API key reference (OPENAI, GROQ, LANGSMITH, HF)
├── CLAUDE.md              # This file
├── docs/
│   └── index.html         # Portfolio webpage — Tailwind, filterable grid, skills matrix
├── ai-gen-bootcamp/       # 16 use-case projects
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
└── ai-agent-bootcamp/     # 8 session-based projects
    ├── session-01-llm-setup/
    ├── session-02-chain-of-thought/
    ├── session-03-rag-fundamentals/
    ├── session-04-text-to-sql/
    ├── session-05-multi-agent-orchestration/
    ├── session-06-browser-automation/
    ├── session-07-crewai-agents/
    └── session-08-autogen-fintech/
```

Each project folder has:
- `README.md` — business problem, Mermaid architecture, tech stack, setup, guardrails, future enhancements
- `requirements.txt` — all deps pinned
- `.env.example` — project-specific keys
- `tests/test_config.py` — pytest suite (syntax, key validation, file presence)

---

## Current Git Status

- Repo has been initialized (`git init`) ← Ashish is working through this step
- Not yet pushed to GitHub
- GitHub Pages not yet enabled

## Remaining Steps (in order)

1. `git init && git add . && git commit` — **in progress now**
2. Create GitHub repo (github.com/new) — name it `ai-portfolio`
3. `git remote add origin https://github.com/YOUR_USERNAME/ai-portfolio.git`
4. `git push -u origin main`
5. Enable GitHub Pages: repo Settings → Pages → Source: `docs/` → Save
6. Replace `YOUR_USERNAME` placeholder in `README.md` and `docs/index.html`
7. Test live URL: `https://YOUR_USERNAME.github.io/ai-portfolio`

---

## Key Decisions Made (don't undo these)

- **All deps pinned** — intentional for reproducibility; don't unpin
- **`pyautogen==0.10.0` only in session-08** — do NOT add `autogen` package; they conflict
- **`pypdf` not `PyPDF2`** — PyPDF2 is deprecated; all projects use `pypdf`
- **`fpdf2` not `fpdf`** — same reason
- **`langchain-openai` added to session-05** — was missing, caused import error with `ChatOpenAI`
- **session-06 scripts 8 and 12** — rewritten as clean stubs (originals had missing dependencies)

---

## Critical Security Note

Project `02-multi-agent-doctor-booking` source directory contained a real `.env` file with live API keys (Groq, OpenAI, HuggingFace, Serper, Tavily, LangChain). Those credentials should be **rotated immediately**:
- https://console.groq.com → regenerate API key
- https://platform.openai.com → regenerate API key
- https://huggingface.co/settings/tokens → regenerate token

---

## What Was Fixed (audit findings resolved)

| Project | Fix Applied |
|---------|------------|
| 11-chest-xray-detection | `client = OpenAI(api_key="")` → proper env loading |
| session-08-autogen-fintech | Removed conflicting `autogen` package |
| session-05-multi-agent-orchestration | Module-level CSV crash → guarded with `os.path.exists` |
| session-06-browser-automation | Missing `data_info` module + `login_error.png` → clean stubs |
| 10-human-activity-recognition | `from scripts.train_lstm import` → `from train_lstm import` |
| session-07, session-08 | `os.environ[KEY] = None` anti-pattern → `raise ValueError` |
| 06-resume-cover-letter-generator | `PyPDF2` → `pypdf` |
| 15-multilingual-chatbot | `fpdf` → `fpdf2`, `PyPDF2` → `pypdf` |
| 03-ai-coding-agent | Duplicate `dotenv==0.9.9` removed |
| 02-multi-agent-doctor-booking | `verify=False` SSL → `verify=True`; bloated pip-freeze requirements cleaned |
| All projects | `os.environ[KEY] = os.getenv(KEY)` → validated with `raise ValueError` |

---

## Validation Results (run in Cowork before handoff)

- ✅ 224 Python files — 0 syntax errors
- ✅ 0 hardcoded API keys
- ✅ 24/24 projects — README, requirements.txt, .env.example, tests all present
- ✅ Portfolio HTML — 49K, all 24 projects, filter logic, skills matrix, contact section
- ⚠️ `pytest tests/` — run locally on Ashish's machine; sandbox recursion limit prevented CI run here

---

## Ashish's Profile (for bio/copy tasks)

- **Name:** Ashish Yadav
- **Email:** ashishk.yadav@gmail.com
- **LinkedIn:** linkedin.com/in/ashishkyadav07
- **Location:** Ontario, Canada
- **Experience:** 19+ years — Alight Solutions (F500 SaaS delivery), Optum/UnitedHealth Group, Hewitt Associates
- **Certs:** PMP, CSM, Google Cloud Generative AI Leader, Azure AI Fundamentals (AZ-900 + AI-900)
- **Agencies:** AYOGI (Salesforce/Odoo for SMBs), Brandnotes (Salesforce enterprise)

---

## Running Any Project Locally

```bash
cd ai-gen-bootcamp/01-autogen-research-agent  # or any project dir
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../../.env.example .env   # then edit .env with real keys
streamlit run app.py          # or whichever entry point the README specifies
pytest tests/                 # run test suite
```
