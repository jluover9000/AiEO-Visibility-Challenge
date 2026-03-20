import asyncio
import re
from typing import Dict, Optional
import openai
from config import OPENAI_API_KEY, GRADING_MODEL, DEFAULT_SCORING_CRITERIA


def _build_default_scoring_system_prompt() -> str:
    """Build a fallback scoring system prompt from DEFAULT_SCORING_CRITERIA."""
    return f"""
You are an expert evaluator of AI responses. Your task is to score the following response on a scale of 0-100.

Evaluation Criteria: {DEFAULT_SCORING_CRITERIA}

You will receive the user's original question and the advisor's response.

Respond in this exact format:
SCORE: [number from 0 to 100]
JUSTIFICATION: [2-3 sentences explaining the score, referencing specific strengths or gaps]
"""


async def score_response(
    question: str,
    response: str,
    scoring_system_prompt: Optional[str] = None,
    grading_model: str = None,
) -> Dict:
    """
    Score a single advisor response using the scoring model.

    Args:
        question: The original user question sent to the advisor models
        response: The advisor model's response to evaluate
        scoring_system_prompt: Full system prompt for the scoring model loaded from
                               scoring_prompts/<name>.md. Falls back to DEFAULT_SCORING_CRITERIA
                               if not provided.
        grading_model: OpenAI model for grading (default: from config)

    Returns:
        {
            "score": 85,
            "justification": "...",
            "grading_model": "gpt-4o-mini",
        }
    """
    if grading_model is None:
        grading_model = GRADING_MODEL

    if not scoring_system_prompt:
        scoring_system_prompt = _build_default_scoring_system_prompt()

    user_message = f"""User Question:
{question}

Advisor Response:
{response}"""

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=grading_model,
            messages=[
                {"role": "system", "content": scoring_system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        result_text = completion.choices[0].message.content

        score_match = re.search(r"SCORE:\s*(\d+\.?\d*)", result_text, re.IGNORECASE)
        justification_match = re.search(
            r"JUSTIFICATION:\s*(.+)", result_text, re.IGNORECASE | re.DOTALL
        )

        score = float(score_match.group(1)) if score_match else 0
        justification = (
            justification_match.group(1).strip() if justification_match else result_text
        )

        score = max(0.0, min(100.0, score))
        score = round(score, 1)

        return {
            "score": score,
            "justification": justification,
            "grading_model": grading_model,
        }

    except Exception as e:
        return {
            "score": None,
            "justification": f"Scoring failed: {str(e)}",
            "grading_model": grading_model,
            "error": str(e),
        }


async def score_all_responses(
    question: str,
    responses: Dict[str, Dict],
    scoring_system_prompt: Optional[str] = None,
) -> Dict:
    """
    Score all three advisor responses in parallel.

    Args:
        question: The original user question sent to the advisor models
        responses: {"openai": {...}, "gemini": {...}, "claude": {...}}
                   Each value is the result dict from the advisor agent
                   (must contain a "response" key with the text).
        scoring_system_prompt: Full system prompt for the scoring model.
                               Falls back to DEFAULT_SCORING_CRITERIA if not provided.

    Returns:
        {
            "openai": {"score": 85, "justification": "...", "rank": 1},
            "gemini": {"score": 72, "justification": "...", "rank": 3},
            "claude": {"score": 80, "justification": "...", "rank": 2},
            "winner": "openai"
        }
    """
    response_texts = {
        "openai": responses.get("openai", {}).get("response", ""),
        "gemini": responses.get("gemini", {}).get("response", ""),
        "claude": responses.get("claude", {}).get("response", ""),
    }

    openai_score_task = score_response(question, response_texts["openai"], scoring_system_prompt)
    gemini_score_task = score_response(question, response_texts["gemini"], scoring_system_prompt)
    claude_score_task = score_response(question, response_texts["claude"], scoring_system_prompt)

    openai_score, gemini_score, claude_score = await asyncio.gather(
        openai_score_task, gemini_score_task, claude_score_task
    )

    model_scores = {
        "openai": openai_score.get("score") or 0,
        "gemini": gemini_score.get("score") or 0,
        "claude": claude_score.get("score") or 0,
    }

    sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)

    ranks = {model: rank for rank, (model, _) in enumerate(sorted_models, start=1)}
    winner = sorted_models[0][0]

    return {
        "openai": {**openai_score, "rank": ranks["openai"]},
        "gemini": {**gemini_score, "rank": ranks["gemini"]},
        "claude": {**claude_score, "rank": ranks["claude"]},
        "winner": winner,
    }
