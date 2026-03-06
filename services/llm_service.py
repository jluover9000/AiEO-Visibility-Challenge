import asyncio
from typing import AsyncGenerator, Dict, List
from datetime import datetime, timezone
import time

import openai
from google import genai
from anthropic import Anthropic

from config import (
    OPENAI_API_KEY,
    GOOGLE_API_KEY,
    ANTHROPIC_API_KEY,
    OPENAI_MODEL,
    GEMINI_MODEL,
    CLAUDE_MODEL,
)


class OpenAIAgent:
    """Agent for OpenAI API with streaming support."""

    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL

    async def generate_response(self, prompt: str):
        """
        Generate response from OpenAI with streaming.

        Args:
            prompt: The input prompt text

        Yields:
            Dicts with streaming chunks and final result
        """
        start_time = time.time()
        full_response = ""
        error = None

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield {"chunk": content, "done": False}

        except Exception as e:
            error = str(e)
            full_response = f"Error: {error}"

        duration = time.time() - start_time

        yield {
            "chunk": "",
            "done": True,
            "result": {
                "model": self.model,
                "response": full_response,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "error": error,
            },
        }


class GeminiAgent:
    """Agent for Google Gemini API with streaming support."""

    def __init__(self):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_name = GEMINI_MODEL

    async def generate_response(self, prompt: str):
        """
        Generate response from Gemini with streaming.

        Args:
            prompt: The input prompt text

        Yields:
            Dicts with streaming chunks and final result
        """
        start_time = time.time()
        full_response = ""
        error = None

        try:
            response = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt
            )

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield {"chunk": chunk.text, "done": False}

        except Exception as e:
            error = str(e)
            full_response = f"Error: {error}"

        duration = time.time() - start_time

        yield {
            "chunk": "",
            "done": True,
            "result": {
                "model": self.model_name,
                "response": full_response,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "error": error,
            },
        }


class ClaudeAgent:
    """Agent for Anthropic Claude API with streaming support."""

    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL

    async def generate_response(self, prompt: str):
        """
        Generate response from Claude with streaming.

        Args:
            prompt: The input prompt text

        Yields:
            Dicts with streaming chunks and final result
        """
        start_time = time.time()
        full_response = ""
        error = None

        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield {"chunk": text, "done": False}

        except Exception as e:
            error = str(e)
            full_response = f"Error: {error}"

        duration = time.time() - start_time

        yield {
            "chunk": "",
            "done": True,
            "result": {
                "model": self.model,
                "response": full_response,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "error": error,
            },
        }


async def process_prompts_parallel(prompts: List[Dict]) -> Dict:
    """
    Send each prompt to all 3 LLMs in parallel and collect responses.

    Args:
        prompts: List of dicts with 'filename' and 'content' keys

    Returns:
        Dict with session data including all prompts and their responses
    """
    openai_agent = OpenAIAgent()
    gemini_agent = GeminiAgent()
    claude_agent = ClaudeAgent()

    results = {
        "session_id": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "prompts": [],
    }

    for prompt_data in prompts:
        prompt_result = {
            "filename": prompt_data["filename"],
            "content": prompt_data["content"],
            "responses": {"openai": {}, "gemini": {}, "claude": {}},
        }

        async def collect_openai():
            generator = openai_agent.generate_response(prompt_data["content"])
            async for update in generator:
                if update.get("done"):
                    break
                yield ("openai", update)
            result = await generator.asend(None)
            prompt_result["responses"]["openai"] = result

        async def collect_gemini():
            generator = gemini_agent.generate_response(prompt_data["content"])
            async for update in generator:
                if update.get("done"):
                    break
                yield ("gemini", update)
            result = await generator.asend(None)
            prompt_result["responses"]["gemini"] = result

        async def collect_claude():
            generator = claude_agent.generate_response(prompt_data["content"])
            async for update in generator:
                if update.get("done"):
                    break
                yield ("claude", update)
            result = await generator.asend(None)
            prompt_result["responses"]["claude"] = result

        results["prompts"].append(prompt_result)

    return results
