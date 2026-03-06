# Multi-LLM Prompt Tester with Automatic Scoring

A Streamlit web application that allows you to test prompts across multiple Large Language Models (OpenAI, Google Gemini, and Anthropic Claude) simultaneously. View real-time streaming responses side-by-side, get automatic AI-powered scoring and ranking, and save results to JSON logs.

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
    Prompt[Upload .md Prompt] -->|Parse| ExtractPersona[Extract Persona Header]
    ExtractPersona -->|persona_name or None| LoadPersona[Load Persona File]
    LoadPersona -->|Persona Content| PrepareMessages[Prepare Messages]
    
    PrepareMessages -->|System: Persona + User: Clean Prompt| OpenAI[OpenAI Agent]
    PrepareMessages -->|System: Persona + User: Clean Prompt| Gemini[Gemini Agent]
    PrepareMessages -->|System: Persona + User: Clean Prompt| Claude[Claude Agent]
    
    OpenAI --> Responses[Collect Responses]
    Gemini --> Responses
    Claude --> Responses
    
    Responses --> Scorer[Scoring Agent]
    LoadPersona -.->|Include in scoring context| Scorer
    
    Scorer -->|Persona-aware scores| Display[Display Results]
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
