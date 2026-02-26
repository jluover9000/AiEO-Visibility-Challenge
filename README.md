# Multi-LLM Prompt Tester

A Streamlit web application that allows you to test prompts across multiple Large Language Models (OpenAI, Google Gemini, and Anthropic Claude) simultaneously. View real-time streaming responses side-by-side and save results to JSON logs with optional S3 upload.

## Architecture

```
User Upload (.md files) 
    ↓
Streamlit Frontend
    ↓
File Handler (parse .md)
    ↓
LLM Orchestrator (parallel processing)
    ├→ OpenAI Agent
    ├→ Gemini Agent  
    └→ Claude Agent
    ↓
Real-time Display (3-column layout)
    ↓
JSON Logger
    ├→ Download locally
```

## Prerequisites

- Python 3.11+
- API keys for:
  - OpenAI
  - Google Gemini
  - Anthropic Claude
- AWS account (optional, for S3 uploads)
