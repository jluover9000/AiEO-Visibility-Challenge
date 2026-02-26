# Multi-LLM Prompt Tester

A Streamlit web application that allows you to test prompts across multiple Large Language Models (OpenAI, Google Gemini, and Anthropic Claude) simultaneously. View real-time streaming responses side-by-side and save results to JSON logs with optional S3 upload.

## Features

- 🤖 **Multi-LLM Support**: Test prompts with OpenAI GPT-4, Google Gemini, and Anthropic Claude simultaneously
- ⚡ **Real-time Streaming**: Watch responses stream in real-time across all three models
- 📁 **Batch Processing**: Upload multiple .md files and process them all at once
- 💾 **JSON Logging**: Save all responses with metadata (model, duration, timestamp) as structured JSON
- ☁️ **S3 Integration**: Automatically upload logs to AWS S3 bucket
- 🔒 **Password Protection**: Simple authentication to control access
- 📊 **Side-by-side Comparison**: View all three model responses in parallel columns

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
    └→ Upload to S3
```

## Prerequisites

- Python 3.11+
- API keys for:
  - OpenAI
  - Google Gemini
  - Anthropic Claude
- AWS account (optional, for S3 uploads)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/multi-llm-prompt-tester.git
cd multi-llm-prompt-tester
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# LLM API Keys
OPENAI_API_KEY=your-openai-key-here
GOOGLE_API_KEY=your-google-api-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# App Configuration
APP_PASSWORD=your-secure-password-here

# AWS S3 Configuration (optional)
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1

# Model Configuration (optional overrides)
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-1.5-pro
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

## Usage

### Running Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Run the Streamlit app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Application

1. **Login**: Enter the password configured in your `.env` file
2. **Upload Files**: Click "Upload Markdown Files" and select one or more `.md` files
3. **Process**: Click "🚀 Process Prompts" to send prompts to all three LLMs
4. **View Results**: Watch real-time streaming responses in three columns
5. **Download**: Click "💾 Download JSON Log" to save results locally
6. **Upload to S3** (optional): Click "☁️ Upload to S3" to save to your S3 bucket

### Sample Test Files

Test prompts are provided in the `test_prompts/` directory:

- `sample_prompt_1.md` - Creative writing prompt
- `sample_prompt_2.md` - Technical explanation prompt

## Project Structure

```
.
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration and environment variables
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── services/
│   ├── __init__.py
│   ├── auth_service.py        # Password authentication
│   ├── file_handler.py        # .md file processing
│   ├── llm_service.py         # LLM agent implementations
│   └── logger_service.py      # JSON logging and S3 upload
├── deployment/
│   └── aws_setup.md          # AWS deployment guide
└── test_prompts/
    ├── sample_prompt_1.md
    └── sample_prompt_2.md
```

## AWS Deployment

For production deployment on AWS EC2 with S3 storage, see the detailed guide:

📖 [AWS Deployment Guide](deployment/aws_setup.md)

Key steps:
1. Create S3 bucket for log storage
2. Set up IAM role with S3 permissions
3. Launch EC2 t3.small instance
4. Configure security groups
5. Install dependencies and run app
6. Optional: Set up Nginx reverse proxy with SSL

## JSON Log Format

Results are saved in the following structure:

```json
{
  "session_id": "20260226_143000",
  "timestamp": "2026-02-26T14:30:00Z",
  "prompts": [
    {
      "filename": "prompt1.md",
      "content": "Write a story about...",
      "responses": {
        "openai": {
          "model": "gpt-4o",
          "response": "Once upon a time...",
          "duration_seconds": 3.5,
          "timestamp": "2026-02-26T14:30:05Z",
          "error": null
        },
        "gemini": { ... },
        "claude": { ... }
      }
    }
  ]
}
```

## Configuration Options

### Model Selection

Override default models in `.env`:

```env
OPENAI_MODEL=gpt-4o-mini
GEMINI_MODEL=gemini-1.5-flash
CLAUDE_MODEL=claude-3-opus-20240229
```

### S3 Configuration

To enable S3 uploads, configure:

```env
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
```

Ensure your EC2 instance has an IAM role with S3 write permissions, or configure AWS credentials locally.

## Security Considerations

- ✅ API keys stored in `.env` (never committed to git)
- ✅ Password protection via `APP_PASSWORD`
- ✅ S3 permissions via IAM roles (no hardcoded credentials)
- ⚠️ Use HTTPS in production (Nginx + Let's Encrypt)
- ⚠️ Restrict security group access to known IPs

## Cost Estimates

### LLM API Costs (varies by usage)
- OpenAI GPT-4o: ~$2.50-$10 per 1M input tokens
- Google Gemini Pro: ~$0.50-$2 per 1M input tokens
- Claude 3.5 Sonnet: ~$3-$15 per 1M input tokens

### AWS Infrastructure (monthly)
- EC2 t3.small: ~$15
- EBS 20GB: ~$2
- S3 storage: ~$0.023/GB
- **Total**: ~$20-25/month

## Troubleshooting

### API Key Errors

```bash
# Verify .env file exists and has correct format
cat .env

# Check if keys are loaded
python3 -c "from config import *; print('OpenAI:', OPENAI_API_KEY[:10])"
```

### Streamlit Not Starting

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Run with verbose logging
streamlit run app.py --logger.level=debug
```

### S3 Upload Fails

- Verify IAM role attached to EC2 instance
- Check bucket name and region in `.env`
- Test AWS credentials: `aws s3 ls s3://your-bucket-name/`
- Logs will fall back to local download on S3 failure

## Development

### Adding New LLM Providers

1. Add API key to `config.py`
2. Create new agent class in `services/llm_service.py`
3. Add to orchestrator in `process_prompts_parallel()`
4. Update UI in `app.py` to add new column

### Running Tests

```bash
# Test with sample files
streamlit run app.py

# Upload test_prompts/sample_prompt_1.md
# Verify all three models respond
# Check JSON log format
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use and modify

## Support

For issues or questions:
- Check the [AWS Deployment Guide](deployment/aws_setup.md)
- Review [Streamlit Documentation](https://docs.streamlit.io/)
- Open an issue on GitHub

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [OpenAI API](https://platform.openai.com/) - GPT models
- [Google Gemini](https://ai.google.dev/) - Gemini models
- [Anthropic API](https://www.anthropic.com/) - Claude models
- [Boto3](https://boto3.amazonaws.com/) - AWS SDK for Python

---

Made with ❤️ for comparing LLM responses
