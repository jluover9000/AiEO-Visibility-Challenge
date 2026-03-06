# Multi-LLM Prompt Tester with Automatic Scoring

A Streamlit web application that allows you to test prompts across multiple Large Language Models (OpenAI, Google Gemini, and Anthropic Claude) simultaneously. View real-time streaming responses side-by-side, get automatic AI-powered scoring and ranking, and save results to JSON logs with optional S3 upload.

## Features

- **Multi-LLM Support**: Test with OpenAI GPT-4, Google Gemini, and Anthropic Claude simultaneously
- **Persona System**: Apply specialized personas (Canadian Business Advisor, Educational Counselor) to shape LLM responses
- **Real-time Streaming**: Watch responses stream in real-time across all three models
- **Automatic Scoring**: AI-powered evaluation and ranking of responses using model-graded scoring
- **Winner Detection**: Automatically identifies the best response based on scoring criteria
- **Batch Processing**: Upload multiple .md files and process them all at once
- **JSON Logging**: Save all responses, scores, and rankings as structured JSON
- **Flexible Criteria**: Define custom scoring criteria in your prompts or use defaults
- **Password Protection**: Simple authentication to control access
- **Comparison Table**: View scores and ranks side-by-side

## Architecture

```mermaid
flowchart TD
    Prompt[Upload .md Prompt] -->|Parse| Extract[Extract Scoring Criteria]
    Extract -->|Optional criteria| LLMs[3 LLMs Generate Responses]
    
    LLMs -->|OpenAI Response| Scorer1[Inspect-AI Scorer]
    LLMs -->|Gemini Response| Scorer2[Inspect-AI Scorer]
    LLMs -->|Claude Response| Scorer3[Inspect-AI Scorer]
    
    Scorer1 -->|Model-graded| Score1[Score + Justification]
    Scorer2 -->|Model-graded| Score2[Score + Justification]
    Scorer3 -->|Model-graded| Score3[Score + Justification]
    
    Score1 -->|Aggregate| Table[Comparison Table]
    Score2 -->|Aggregate| Table
    Score3 -->|Aggregate| Table
    
    Table -->|Display| UI[Streamlit UI]
    Table -->|Include| JSONLog[JSON Download]
    Table -->|Identify| Winner[Highlight Winner]
```

## Available Personas

The system includes specialized personas that shape how LLMs respond:

- **canadian_business_startup**: Expert business advisor for starting businesses in Canada
- **educational_counselor**: Canadian education and scholarship advisor for students

Personas are optional. Without a persona, LLMs respond in their default mode.

## Prerequisites

- Python 3.11+
- API keys for:
  - OpenAI
  - Google Gemini
  - Anthropic Claude
- AWS account (optional, for S3 uploads)
