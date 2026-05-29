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

- Repo: `git@github.com:ashishk-yadav/AI-portfolio.git`
- Branch: `main` — all changes pushed
- GitHub Pages: enabled at `https://ashishk-yadav.github.io/AI-portfolio`
- SSH key: `~/.ssh/github_mac` (use `GIT_SSH_COMMAND="ssh -i ~/.ssh/github_mac" git push`)

## Remaining Steps

1. Deploy all 21 Streamlit Cloud apps — see deployment table below
2. Deploy 3 HuggingFace Spaces apps (projects 10, 11, 12)
3. Update `demo:` URLs in `docs/index.html` once live URLs are known

---

## Key Decisions Made (don't undo these)

- **All deps pinned** — intentional for reproducibility; don't unpin
- **`pyautogen` removed from project 01** — AG2 rebranding broke `from autogen import`; replaced with direct Groq SDK
- **`pyautogen==0.10.0` only in session-08** — do NOT add `autogen` package; they conflict
- **`pypdf` not `PyPDF2`** — PyPDF2 is deprecated; all projects use `pypdf`
- **`fpdf2` not `fpdf`** — same reason
- **`langchain-openai` added to session-05** — was missing, caused import error with `ChatOpenAI`
- **session-06 scripts 8 and 12** — rewritten as clean stubs (originals had missing dependencies)
- **`runtime.txt` at repo root** — pins Python 3.11 for all Streamlit Cloud deployments; never remove

---

## Pre-Deployment Checklist

Run every check below before deploying any project to Streamlit Cloud or HuggingFace Spaces.
Learned from live deployment failures — each item maps to a real bug.

---

### 1. Python Version

- [ ] `runtime.txt` exists at **repo root** with content `python-3.11`
- [ ] Never rely on the platform's default Python — Streamlit Cloud has used 3.14 which breaks most ML/AI packages

---

### 2. requirements.txt — Version Existence

Every pinned version must actually exist on PyPI. Verify with:

```bash
curl -s "https://pypi.org/pypi/<package>/<version>/json" -o /dev/null -w "%{http_code}"
# 200 = exists, 404 = does not exist → deployment will fail
```

**Lessons learned:**
- `pyautogen==0.9.9` — never released (skipped; valid range was `0.2.x` and `0.10.0`)
- Never guess or copy version numbers — look them up on pypi.org

---

### 3. requirements.txt — Python 3.11 Compatibility

Check `requires_python` for each complex package:

```bash
curl -s "https://pypi.org/pypi/<package>/<version>/json" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d['info'].get('requires_python','any'))"
```

**Known constraints to watch:**
| Package | Constraint | Safe on 3.11? |
|---------|-----------|---------------|
| `crewai>=0.80` | `<=3.13,>=3.10` | ✓ |
| `pyautogen==0.10.0` | `>=3.10` | ✓ |
| `numpy>=2.3` | `>=3.11` | ✓ exactly |
| `scikit-learn>=1.7` | `>=3.10` | ✓ |
| `pyautogen 0.2.x` | `<3.13` | ✓ |

---

### 4. requirements.txt — Completeness

**Every `import X` in every `.py` file the app touches must have a corresponding package in requirements.txt.**
Do NOT rely on transitive dependencies — they are not guaranteed.

Audit steps:
1. Open the Streamlit entry point (e.g., `app.py`)
2. List every `import` and `from X import` — both at top-level and inside functions
3. Follow every `from local_module import` — open that module and repeat
4. For each import, confirm the PyPI package name is in requirements.txt

**Known tricky misses from this project:**

| Import statement | PyPI package needed | Common mistake |
|-----------------|--------------------|----|
| `from docx import Document` | `python-docx` | confusing import name |
| `from jinja2 import Template` | `Jinja2` | often arrives transitively via streamlit — fragile |
| `import chromadb` | `chromadb` | easy to miss when using via LangChain wrapper |
| `from scholarly import scholarly` | `scholarly` | was in code but never in requirements |
| `import PyPDF2` | **use `pypdf` instead** | PyPDF2 is deprecated |
| `from fpdf import FPDF` | `fpdf2` (not `fpdf`) | import name ≠ PyPI name |
| `import PIL` | `Pillow` | import name ≠ PyPI name |

**Remove unused packages** — they slow installs and can introduce conflicts:
- Anything leftover after a rewrite (e.g., `fastapi`/`uvicorn` after switching from FastAPI to standalone Streamlit)
- Packages used only in commented-out code paths

---

### 5. Package Naming Gotchas

PyPI package name ≠ Python import name in several cases:

| PyPI install name | Python import | Notes |
|------------------|--------------|-------|
| `python-docx` | `from docx import Document` | |
| `Pillow` | `import PIL` | |
| `fpdf2` | `from fpdf import FPDF` | do NOT use `fpdf` (unmaintained) |
| `pypdf` | `from pypdf import PdfReader` | replaces deprecated `PyPDF2` |
| `scikit-learn` | `import sklearn` | |
| `beautifulsoup4` | `from bs4 import BeautifulSoup` | |
| `opencv-python` | `import cv2` | |

**Rebranded/broken packages:**
- `pyautogen>=0.10.0` — AG2 rebranding; `from autogen import AssistantAgent` no longer works reliably → use the direct SDK (Groq, OpenAI) instead
- `PyPDF2` — deprecated; use `pypdf`
- `fpdf` — unmaintained; use `fpdf2`

---

### 6. Code Architecture — Import Safety

**Rule: No LLM client must be created, and no key must be read, before `_require_keys()` runs.**

Checklist:
- [ ] `st.set_page_config()` is the **first** Streamlit call in the script (before any `st.*`)
- [ ] `_require_keys()` is defined and called **before** any local module import that touches an LLM client
- [ ] No `client = OpenAI()` / `client = Groq()` at module level — move into a function or class `__init__`
- [ ] No `raise ValueError("KEY not set")` at module level — replace with `_require_keys()` pattern
- [ ] No `crew.kickoff()`, `chain.run()`, or any LLM call at module level

**`_require_keys` canonical pattern** (copy-paste for every new app):

```python
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="...", page_icon="...")

def _require_keys(*pairs):
    needed = [(k, lbl, ph) for k, lbl, ph in pairs if not os.getenv(k)]
    if not needed:
        return
    with st.sidebar:
        st.markdown("---")
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
    ("OPENAI_API_KEY", "OpenAI API Key", "sk-..."),
    # ("GROQ_API_KEY", "Groq API Key", "gsk_..."),   # add as needed
)

# ALL local module imports go AFTER this line
from my_module import MyClass
```

---

### 7. Code Architecture — Cloud Compatibility

- [ ] No calls to `localhost` / `127.0.0.1` — the app must be fully self-contained (no local FastAPI backend, no local model server)
- [ ] No `selenium` / browser automation — Streamlit Cloud has no display server
- [ ] No training code in the Streamlit entry point — training must be offline; app only does inference
- [ ] No hardcoded file paths — use relative paths or `os.path.join`
- [ ] No `input()` calls — Streamlit is not a terminal

---

### 8. Instance-Level Bugs to Check

- [ ] Every `self.X` referenced in a method is set in `__init__` — common miss when a feature is half-removed
- [ ] No bare `except:` swallowing real errors silently — use `except Exception as e: st.error(str(e))`
- [ ] All agent/chain objects that depend on an API key are created **lazily** (inside button handlers or `@st.cache_resource` functions), not at app startup

---

### 9. Pre-Deploy Smoke Test (local)

```bash
cd <project-dir>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # must complete with 0 errors
python -c "import <main_module>"         # catches import-time crashes
streamlit run app.py                     # open in browser, verify sidebar key prompt appears before any crash
```

Verify:
- [ ] App loads with NO env keys set — sidebar shows key prompt, does not crash
- [ ] After entering a valid key, the main UI renders
- [ ] At least one core action (button press) works end-to-end

---

## Critical Security Note

Project `02-multi-agent-doctor-booking` source directory contained a real `.env` file with live API keys (Groq, OpenAI, HuggingFace, Serper, Tavily, LangChain). Those credentials should be **rotated immediately**:
- https://console.groq.com → regenerate API key
- https://platform.openai.com → regenerate API key
- https://huggingface.co/settings/tokens → regenerate token

---

## What Was Fixed (audit findings resolved)

### Initial audit
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

### Runtime key collection (all 24 apps)
| Scope | Fix Applied |
|-------|------------|
| All 16 existing Streamlit entry points | Added `_require_keys()` pattern — sidebar key prompt, lazy local imports |
| 02-multi-agent-doctor-booking | Full rewrite: FastAPI backend → standalone LangChain/Groq app |
| session-07-crewai-agents | Full rewrite: `crew.kickoff()` at module level → button handler |
| session-08-autogen-fintech | Agents moved from module level into `run_analysis()` function |
| 7 CLI-only projects (08, 09, S01–S06) | New `app.py` Streamlit wrapper files created |

### Deployment bug fixes (found during live Streamlit Cloud deploy)
| Project | Bug | Fix |
|---------|-----|-----|
| All projects | Streamlit Cloud defaulted to Python 3.14, breaking most packages | Added `runtime.txt` → `python-3.11` at repo root |
| 01-autogen-research-agent | `pyautogen==0.9.9` doesn't exist on PyPI | Changed to `0.10.0` then removed entirely |
| 01-autogen-research-agent | `pyautogen==0.10.0` AG2 rebranding — `from autogen import` broken | Rewrote `agents.py` using Groq SDK directly |
| 01-autogen-research-agent | `from scholarly import scholarly` — package not in requirements | Removed (unused in main code path) |
| 01-autogen-research-agent | `self.search_agent` used but never set in `DataLoader.__init__` | Removed broken expansion logic |
| 06-resume-cover-letter-generator | `python-docx` missing (app uses `from docx import Document`) | Added `python-docx==1.1.2` |
| 06-resume-cover-letter-generator | `Jinja2` missing (prompts.py uses jinja2.Template) | Added `Jinja2==3.1.4` |
| 06-resume-cover-letter-generator | `PyPDF2` used in code, only `pypdf` in requirements | Changed to `from pypdf import PdfReader` |
| session-05-multi-agent-orchestration | `chromadb` missing (LangChain Chroma needs it directly) | Added `chromadb==0.5.20` |
| session-05-multi-agent-orchestration | `yfinance` in requirements, unused by the app | Removed |

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

---

## Docker / OrbStack Deployment (Next Phase)

**Decision made in Cowork session (2026-05-28). Build this next.**

### Architecture

All 24 projects run as Docker containers on the Mac Mini — no Streamlit Cloud, no HuggingFace Spaces. Zero cold starts. Remote access via Tailscale.

**Hardware:** Mac Mini 2023, M2 (Apple Silicon), 16 GB unified RAM, 1 TB storage  
**Docker runtime:** OrbStack (not Docker Desktop) — native ARM64, near-zero overhead  
**Remote access:** Tailscale already installed and configured  

### Two-Tier Compose Profiles

| Profile | Projects | RAM est. | When |
|---------|----------|----------|------|
| `core` | 20 light/medium apps (all except 09, 10, 11, 12) | ~5.5 GB | Always running (`restart: unless-stopped`) |
| `ml` | 09-image-captioning, 10-human-activity-recognition, 11-chest-xray-detection, 12-neural-style-transfer | ~3–4 GB | Start before ML demos, stop after |

Start commands:
```bash
docker compose --profile core up -d       # boot the always-on 20
docker compose --profile ml up -d         # boot heavy ML apps before demo
docker compose --profile ml stop          # stop after demo
```

### Critical: Bake Model Weights into Docker Images

For projects 09, 10, 11, 12 — download model weights at `docker build` time, not at runtime.
This eliminates the cold start for model loading. Example pattern:

```dockerfile
# In Dockerfile for project 11
RUN python -c "
import torchvision.models as models
models.vgg16(weights='IMAGENET1K_V1')
"
```

Each project's weights download once on first build, live in the image layer forever.

### ARM64 / Apple Silicon Notes

- OrbStack runs containers as native `linux/arm64` — no QEMU emulation, near-native performance
- PyTorch in containers does NOT get Apple MPS (Metal GPU) — CPU inference only
- For demo purposes this is fine: project 11 ~3–5 sec/inference, project 12 ~30–60 sec/image (frame as "watch the model work")
- Use `--platform linux/arm64` in all Dockerfiles

### Port Mapping Convention

Assign ports sequentially so they're predictable:

| Port | Project |
|------|---------|
| 8501 | 01-autogen-research-agent |
| 8502 | 02-multi-agent-doctor-booking |
| 8503 | 03-ai-coding-agent |
| 8504 | 04-customer-service-agent |
| 8505 | 05-product-sentiment-classifier |
| 8506 | 06-resume-cover-letter-generator |
| 8507 | 07-marketing-copy-generator |
| 8508 | 08-finetune-tinyllama |
| 8509 | 09-image-captioning-cnn-lstm |
| 8510 | 10-human-activity-recognition |
| 8511 | 11-chest-xray-detection |
| 8512 | 12-neural-style-transfer |
| 8513 | 13-legal-doc-summarizer |
| 8514 | 14-news-topic-classifier |
| 8515 | 15-multilingual-chatbot |
| 8516 | 16-document-qna-rag |
| 8601 | session-01-llm-setup |
| 8602 | session-02-chain-of-thought |
| 8603 | session-03-rag-fundamentals |
| 8604 | session-04-text-to-sql |
| 8605 | session-05-multi-agent-orchestration |
| 8606 | session-06-browser-automation |
| 8607 | session-07-crewai-agents |
| 8608 | session-08-autogen-fintech |

### Files to Create

1. **`Dockerfile`** (shared base template — copy/adapt per project):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

2. **`docker-compose.yml`** at repo root — all 24 services, profiles, port mapping, shared `.env`

3. **`.env`** at repo root (gitignored) — single source of truth for all API keys across all containers

4. **`build_all.sh`** — builds all 24 images (run once, or after deps change)

5. **`README-docker.md`** — quick-start for Docker workflow

### API Keys — Shared .env Pattern

Mount the root `.env` into every container so keys are managed in one place:

```yaml
# In docker-compose.yml, per service:
env_file:
  - .env
```

### Tailscale Access

Once containers are running, access from any Tailscale device:
- `http://<mac-mini-tailscale-ip>:8501` — project 01
- `http://<mac-mini-tailscale-ip>:8608` — session 08
- No extra config needed — OrbStack exposes ports on all interfaces by default

### What to Build (Claude Code task)

1. Write a `Dockerfile` for each of the 24 projects (adapt entry point per project — see CLAUDE.md Repo Structure for which file is the Streamlit entry point per project)
2. Write `docker-compose.yml` with all 24 services, correct profiles, port mapping above
3. Write `build_all.sh` — iterates all projects and runs `docker build`
4. Test: `docker compose --profile core up -d` — verify all 20 core containers start and are reachable
5. Test: `docker compose --profile ml up -d` — verify 4 ML containers start and models load
6. Update `docs/index.html` demo links to point to `http://localhost:<port>` for local use

---

## Current State (as of 2026-05-29)

### Infrastructure — DONE

| Component | Status | Detail |
|-----------|--------|--------|
| 24 Docker containers | ✅ Running | OrbStack on Mac Mini M2 |
| docker-compose.yml | ✅ | Two profiles: `core` (20 apps) + `ml` (4 apps) |
| nginx reverse proxy | ✅ Running | Port 80, serves dashboard + proxies all 24 apps |
| dashboard.html | ✅ Live | `http://localhost/` — card grid, status dots, Launch buttons |
| Cloudflare Tunnel | ⏸️ Parked | Config in compose, awaiting domain on Cloudflare |
| Streamlit Cloud | 01, 03 live | `https://01-autogen-research-agent.streamlit.app/` etc. |

### Key Infrastructure Decisions

- **All apps use `--server.baseUrlPath=/app/NN`** set via `command:` in docker-compose.yml (not in Dockerfile CMD — cache issue). This is what makes nginx sub-path proxying work.
- **Dashboard served by nginx** — use `http://localhost/` not `file://`. Launch buttons use relative paths (`/app/01/`) in proxy mode.
- **API keys** — single `.env` at repo root mounted into all containers. Contains: `OPENAI_API_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`, `HUGGINGFACE_TOKEN`, `HF_TOKEN`, `LANGSMITH_API_KEY`, `SCRAPINGDOG_API_KEY`, `CLOUDFLARE_TUNNEL_TOKEN`.
- **llm_provider.py** — provider-agnostic sidebar (OpenAI/Groq/Anthropic) exists in `shared/` and is copied to each project that needs it.

### Entry Points (verified from filesystem)

| Container | Entry Point | Port |
|-----------|------------|------|
| 01-research-assistant | `app.py` | 8501 |
| 02-doctor-booking | `streamlit_ui.py` | 8502 |
| 03-ai-coding-agent | `main.py` | 8503 |
| 04-customer-service-agent | `app.py` | 8504 |
| 05-sentiment-classifier | `app.py` | 8505 |
| 06-resume-generator | `app/app.py` | 8506 |
| 07-marketing-copy | `app.py` | 8507 |
| 08-finetune-tinyllama | `app.py` | 8508 |
| 09-image-captioning | `app.py` | 8509 |
| 10-activity-recognition | `streamlit_compare_model.py` | 8510 |
| 11-xray-detection | `streamlit_app.py` | 8511 |
| 12-neural-style-transfer | `streamlit_app.py` | 8512 |
| 13-legal-summarizer | `app.py` | 8513 |
| 14-news-classifier | `streamlit_app.py` | 8514 |
| 15-multilingual-chatbot | `main.py` | 8515 |
| 16-document-qna-rag | `streamlit_app.py` | 8516 |
| s1-llm-setup | `app.py` | 8601 |
| s2-chain-of-thought | `app.py` | 8602 |
| s3-rag-fundamentals | `app.py` | 8603 |
| s4-text-to-sql | `app.py` | 8604 |
| s5-multi-agent-orchestration | `2.master_agent_ui.py` | 8605 |
| s6-browser-automation | `app.py` | 8606 |
| s7-crewai-agents | `6.multi_debate_system.py` | 8607 |
| s8-autogen-fintech | `3.fintech_app.py` | 8608 |

### App Test Status

| # | Name | Status | Fix Applied |
|---|------|--------|-------------|
| 01 | Research Assistant | ✅ Confirmed | OpenAlex API, Unicode fix, Enter-to-search |
| 02 | Doctor Booking | 🔄 Retest | Provider sidebar added (was Groq-only hardcoded) |
| 03 | AI Coding Agent | ✅ Confirmed | — |
| 04 | Customer Service Agent | 🔄 Retest | LangChain agent → direct RAG pipeline; ChromaDB EphemeralClient |
| 05 | Sentiment Classifier | 🔄 Retest | Auto-init SQLite DB; sample CSV; SerpAPI instructions |
| 06 | Resume Generator | ✅ Confirmed | — |
| 07 | Marketing Copy | 🔄 Retest | Added missing matplotlib==3.9.2 |
| 08 | Fine-Tune TinyLlama | ⬜ Not tested | |
| 09 | Image Captioning | ⬜ Not tested | |
| 10 | Activity Recognition | ✅ Confirmed | — |
| 11 | X-Ray Detection | ⬜ Not tested | |
| 12 | Neural Style Transfer | ✅ Confirmed | — |
| 13 | Legal Summarizer | 🔄 Retest | PyPDF2 → pypdf in utils/io.py |
| 14 | News Classifier | ⬜ Not tested | |
| 15 | Multilingual Chatbot | ✅ Confirmed | — |
| 16 | Document Q&A (RAG) | ✅ Confirmed | OpenAIEmbeddings type hint → Any |
| S1 | LLM Setup | ✅ Confirmed | — |
| S2 | Chain-of-Thought | ✅ Confirmed | — |
| S3 | RAG Fundamentals | 🔄 Retest | ChromaDB EphemeralClient; vectorstore cached in session_state |
| S4 | Text-to-SQL | ✅ Confirmed | — |
| S5 | Multi-Agent Orchestration | ⬜ Not tested | |
| S6 | Browser Automation | ⬜ Not tested | |
| S7 | CrewAI Agents | 🔄 Retest | langchain_community → langchain_openai; module-level crash fixed |
| S8 | AutoGen FinTech | 🔄 Retest | pyautogen broken → direct OpenAI two-stage pipeline |

### Fixes Applied During Docker Testing

| Project | Bug | Fix |
|---------|-----|-----|
| All 24 | Dockerfile CMD syntax error (missing `\` continuation) | Fixed all 24 Dockerfiles |
| All 24 | `--server.baseUrlPath` not propagating (Docker cache) | Added `command:` override in docker-compose.yml |
| All 24 | Dashboard Launch buttons opened current page (`href="#"` async race) | Set href at render time in buildCard() |
| All apps via nginx | White tab — static assets 404 without baseUrlPath | Fixed by `command:` override getting baseUrlPath into containers |
| 01 | `anthropic==0.49.0` conflicts with `langchain-anthropic==0.3.15` | Bumped to `anthropic==0.52.0` across 9 projects |
| 01 | `wordcloud` needs build-essential (C headers) | Added `apt-get install build-essential` to Dockerfile |
| 01 | BLIP pre-download step wrong (app uses HF Inference API) | Removed transformers pre-download from Dockerfile |
| 02 | Groq-only hardcoded, invalid key | Added llm_provider.py, provider sidebar, removed fastapi/uvicorn deps |
| 04 | LangChain agent parse failures; ChromaDB tenant bug | Replaced initialize_agent with direct RAG→LLM pipeline |
| 05 | No test data for 3 input modes | Auto-init SQLite, sample CSV, SerpAPI instructions |
| 07 | `matplotlib` missing from requirements | Added `matplotlib==3.9.2` |
| 08 | BLIP pre-download → wrong (uses HF API) | Removed from Dockerfile |
| 13 | `import PyPDF2` (not installed, replaced by pypdf) | `from pypdf import PdfReader` |
| 16 | `OpenAIEmbeddings` used as type hint, never imported | Changed to `Any` |
| S3 | ChromaDB `default_tenant` error on repeated questions | EphemeralClient + vectorstore cached in session_state |
| S7 | `from langchain_community.chat_models import ChatOpenAI` broken | `from langchain_openai import ChatOpenAI` |
| S8 | `from autogen import` broken (AG2 rebranding) | Direct OpenAI Analyst→Writer pipeline |

### Remaining Work

1. **Retest** apps marked 🔄 (02, 04, 05, 07, 13, S3, S7, S8)
2. **Test** apps marked ⬜ (08, 09, 11, 14, S5, S6)
3. **Cloudflare Tunnel** — add domain to Cloudflare, get tunnel token, add to `.env`, start `cloudflare-tunnel` container
4. **Portfolio HTML** (`docs/index.html`) — update demo URLs for any additional Streamlit Cloud deployments
5. **Docker daily ops**:
   ```bash
   # Start everything
   docker compose --profile core up -d
   docker compose --profile ml up -d   # before ML demos
   # Logs
   docker compose logs -f <container-name>
   # Rebuild one app after a fix
   docker compose build <service> && docker compose up -d --force-recreate <service>
   ```
