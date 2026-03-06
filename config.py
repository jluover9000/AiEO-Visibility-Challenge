import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

APP_PASSWORD = os.getenv("APP_PASSWORD")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

GRADING_MODEL = os.getenv("GRADING_MODEL", "gpt-5-mini")
DEFAULT_SCORING_CRITERIA = os.getenv(
    "DEFAULT_SCORING_CRITERIA",
    "Evaluate the response for accuracy, relevance, and helpfulness on a 0-100 scale.",
)
