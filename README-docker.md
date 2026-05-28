# Docker Deployment — AI Portfolio

## Prerequisites

- [OrbStack](https://orbstack.dev) installed and running
- `.env` file at repo root containing all required API keys (OpenAI, Anthropic, etc.)

---

## First-Time Setup

Build all 24 images (takes a while — ML images include pre-baked model weights):

```bash
chmod +x build_all.sh
./build_all.sh
```

---

## Daily Commands

**Start all 20 core apps:**
```bash
docker compose --profile core up -d
```

**Start 4 ML apps before a demo:**
```bash
docker compose --profile ml up -d
```

**Stop ML apps after a demo (free up RAM/VRAM):**
```bash
docker compose --profile ml stop
```

**Tail logs for a specific app:**
```bash
docker compose logs -f app-01
```

**Stop everything:**
```bash
docker compose down
```

**Rebuild a single app after a code change:**
```bash
docker compose build app-01 && docker compose up -d app-01
```

---

## Port Reference

| Service | Project | Profile | Port | URL |
|---------|---------|---------|------|-----|
| app-01 | 01-autogen-research-agent | core | 8501 | http://localhost:8501 |
| app-02 | 02-multi-agent-doctor-booking | core | 8502 | http://localhost:8502 |
| app-03 | 03-ai-coding-agent | core | 8503 | http://localhost:8503 |
| app-04 | 04-customer-service-agent | core | 8504 | http://localhost:8504 |
| app-05 | 05-product-sentiment-classifier | core | 8505 | http://localhost:8505 |
| app-06 | 06-resume-cover-letter-generator | core | 8506 | http://localhost:8506 |
| app-07 | 07-marketing-copy-generator | core | 8507 | http://localhost:8507 |
| app-08 | 08-finetune-tinyllama | core | 8508 | http://localhost:8508 |
| app-09 | 09-image-captioning-cnn-lstm | ml | 8509 | http://localhost:8509 |
| app-10 | 10-human-activity-recognition | ml | 8510 | http://localhost:8510 |
| app-11 | 11-chest-xray-detection | ml | 8511 | http://localhost:8511 |
| app-12 | 12-neural-style-transfer | ml | 8512 | http://localhost:8512 |
| app-13 | 13-legal-doc-summarizer | core | 8513 | http://localhost:8513 |
| app-14 | 14-news-topic-classifier | core | 8514 | http://localhost:8514 |
| app-15 | 15-multilingual-chatbot | core | 8515 | http://localhost:8515 |
| app-16 | 16-document-qna-rag | core | 8516 | http://localhost:8516 |
| app-s1 | session-01-llm-setup | core | 8601 | http://localhost:8601 |
| app-s2 | session-02-chain-of-thought | core | 8602 | http://localhost:8602 |
| app-s3 | session-03-rag-fundamentals | core | 8603 | http://localhost:8603 |
| app-s4 | session-04-text-to-sql | core | 8604 | http://localhost:8604 |
| app-s5 | session-05-multi-agent-orchestration | core | 8605 | http://localhost:8605 |
| app-s6 | session-06-browser-automation | core | 8606 | http://localhost:8606 |
| app-s7 | session-07-crewai-agents | core | 8607 | http://localhost:8607 |
| app-s8 | session-08-autogen-fintech | core | 8608 | http://localhost:8608 |

---

## Accessing via Tailscale

Replace `localhost` with your Mac Mini's Tailscale IP in any URL above.

Example: `http://100.x.x.x:8501`

Find your Tailscale IP: `tailscale ip -4`

---

## Notes

- All containers use `restart: unless-stopped` — they survive Mac Mini reboots automatically.
- ML images (09-12) have model weights baked in at build time — no cold-start downloads at demo time.
- All services share a single `.env` file at the repo root for API keys.
