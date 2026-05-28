#!/usr/bin/env bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

build() {
  local service="$1"
  local dir="$2"
  echo "Building ${service} (${dir})..."
  docker build --platform linux/arm64 -t "${service}:latest" "${REPO_ROOT}/${dir}"
}

# AI Gen Bootcamp — Core
build app-01 ai-gen-bootcamp/01-autogen-research-agent
build app-02 ai-gen-bootcamp/02-multi-agent-doctor-booking
build app-03 ai-gen-bootcamp/03-ai-coding-agent
build app-04 ai-gen-bootcamp/04-customer-service-agent
build app-05 ai-gen-bootcamp/05-product-sentiment-classifier
build app-06 ai-gen-bootcamp/06-resume-cover-letter-generator
build app-07 ai-gen-bootcamp/07-marketing-copy-generator
build app-08 ai-gen-bootcamp/08-finetune-tinyllama

# AI Gen Bootcamp — ML
build app-09 ai-gen-bootcamp/09-image-captioning-cnn-lstm
build app-10 ai-gen-bootcamp/10-human-activity-recognition
build app-11 ai-gen-bootcamp/11-chest-xray-detection
build app-12 ai-gen-bootcamp/12-neural-style-transfer

# AI Gen Bootcamp — Core (continued)
build app-13 ai-gen-bootcamp/13-legal-doc-summarizer
build app-14 ai-gen-bootcamp/14-news-topic-classifier
build app-15 ai-gen-bootcamp/15-multilingual-chatbot
build app-16 ai-gen-bootcamp/16-document-qna-rag

# AI Agent Bootcamp — Sessions
build app-s1 ai-agent-bootcamp/session-01-llm-setup
build app-s2 ai-agent-bootcamp/session-02-chain-of-thought
build app-s3 ai-agent-bootcamp/session-03-rag-fundamentals
build app-s4 ai-agent-bootcamp/session-04-text-to-sql
build app-s5 ai-agent-bootcamp/session-05-multi-agent-orchestration
build app-s6 ai-agent-bootcamp/session-06-browser-automation
build app-s7 ai-agent-bootcamp/session-07-crewai-agents
build app-s8 ai-agent-bootcamp/session-08-autogen-fintech

echo ""
echo "All images built successfully."
