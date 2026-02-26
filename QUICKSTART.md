# Quick Start Guide

Get your Multi-LLM Prompt Tester running in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- API keys for OpenAI, Google Gemini, and Anthropic Claude
- (Optional) AWS account for S3 storage

## Installation

### Step 1: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Required configuration in `.env`:
```env
OPENAI_API_KEY=your-openai-key-here
GOOGLE_API_KEY=your-google-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
APP_PASSWORD=choose-a-password
```

### Step 2: Quick Start with Script

The easiest way to start:

```bash
./run.sh
```

This script will:
1. Create a virtual environment
2. Install all dependencies
3. Start the Streamlit app

**OR** Manual Installation:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Step 3: Access the App

Open your browser to: **http://localhost:8501**

## First Use

1. **Login** - Enter the password you set in `.env`
2. **Upload** - Select one or more `.md` files (try the samples in `test_prompts/`)
3. **Process** - Click "🚀 Process Prompts"
4. **Watch** - See real-time responses from all three LLMs side-by-side
5. **Download** - Save results as JSON

## Test Files Included

Try these sample prompts to test the system:
- `test_prompts/sample_prompt_1.md` - Creative writing test
- `test_prompts/sample_prompt_2.md` - Technical explanation test

## Project Structure

```
.
├── app.py                    # Main Streamlit app
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── .env                      # Your API keys (create from .env.example)
├── services/
│   ├── auth_service.py      # Authentication
│   ├── file_handler.py      # File processing
│   ├── llm_service.py       # LLM integrations
│   └── logger_service.py    # Logging & S3
├── test_prompts/            # Sample test files
└── deployment/
    └── aws_setup.md         # AWS deployment guide
```

## Next Steps

### Local Development
- Modify prompts in `test_prompts/`
- Adjust models in `.env` (OPENAI_MODEL, GEMINI_MODEL, CLAUDE_MODEL)
- Customize UI in `app.py`

### Production Deployment
Follow the detailed guide: [deployment/aws_setup.md](deployment/aws_setup.md)
- Deploy to AWS EC2 (t3.small)
- Configure S3 for log storage
- Set up SSL with Nginx

## Common Issues

**"Module not found" errors:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"Invalid API key" errors:**
- Check your `.env` file
- Verify keys are active and have quota

**Port 8501 already in use:**
```bash
streamlit run app.py --server.port 8502
```

## Documentation

- **README.md** - Full project documentation
- **TESTING.md** - Complete testing guide
- **deployment/aws_setup.md** - AWS deployment instructions

## Support

For detailed information, see:
- [README.md](README.md) - Complete documentation
- [TESTING.md](TESTING.md) - Testing procedures
- [AWS Setup Guide](deployment/aws_setup.md) - Deployment instructions

## Quick Commands

```bash
# Start the app
./run.sh

# Or manually
source venv/bin/activate
streamlit run app.py

# Install/update dependencies
pip install -r requirements.txt --upgrade

# Check Python version
python3 --version

# Test imports
python3 -c "import streamlit; print('✅ Streamlit installed')"
```

---

**Ready to test your prompts across multiple LLMs? Start now with `./run.sh`!** 🚀
