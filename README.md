# Multi-LLM Prompt Tester with Automatic Scoring

A Streamlit web application that allows you to test prompts across multiple Large Language Models (OpenAI, Google Gemini, and Anthropic Claude) simultaneously. View real-time streaming responses side-by-side, get automatic AI-powered scoring and ranking, and save results to JSON logs with optional S3 upload.

## Features

- 🤖 **Multi-LLM Support**: Test with OpenAI GPT-4, Google Gemini, and Anthropic Claude simultaneously
- ⚡ **Real-time Streaming**: Watch responses stream in real-time across all three models
- 📊 **Automatic Scoring**: AI-powered evaluation and ranking of responses using model-graded scoring
- 🏆 **Winner Detection**: Automatically identifies the best response based on scoring criteria
- 📁 **Batch Processing**: Upload multiple .md files and process them all at once
- 💾 **JSON Logging**: Save all responses, scores, and rankings as structured JSON
- 🎯 **Flexible Criteria**: Define custom scoring criteria in your prompts or use defaults
- 🔒 **Password Protection**: Simple authentication to control access
- 📈 **Comparison Table**: View scores and ranks side-by-side

## Architecture

```
User Upload (.md files) 
    ↓
File Handler (parse .md + extract scoring criteria)
    ↓
LLM Orchestrator (parallel processing)
    ├→ OpenAI Agent
    ├→ Gemini Agent  
    └→ Claude Agent
    ↓
Real-time Display (3-column layout)
    ↓
Scoring Engine (model-graded evaluation)
    ├→ Score each response (0-100 scale)
    ├→ Rank responses (1-3)
    └→ Identify winner
    ↓
Comparison Table + JSON Logger
    ├→ Display scores and justifications
    └→ Download with full scoring data
```

## Prerequisites

- Python 3.11+
- API keys for:
  - OpenAI
  - Google Gemini
  - Anthropic Claude
- AWS account (optional, for S3 uploads)
