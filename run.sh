#!/bin/bash

echo "Multi-LLM Prompt Tester - Startup Script"
echo "========================================="
echo ""

if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

echo "🔄 Activating virtual environment..."
source venv/bin/activate

if [ ! -f "venv/bin/streamlit" ]; then
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
    echo ""
fi

echo "🚀 Starting Streamlit app..."
echo "📍 Access the app at: http://localhost:8501"
echo ""
streamlit run app.py
