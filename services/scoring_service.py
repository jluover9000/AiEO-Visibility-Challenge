import asyncio
import re
from typing import Dict, Optional
import openai
from config import OPENAI_API_KEY, GRADING_MODEL, DEFAULT_SCORING_CRITERIA


async def score_response(
    prompt: str,
    response: str,
    criteria: Optional[str] = None,
    grading_model: str = None,
) -> Dict:
    """
    Score a single LLM response using model-graded evaluation.

    Args:
        prompt: Original input prompt
        response: LLM's response to score
        criteria: Optional scoring criteria (extracted from prompt)
        grading_model: OpenAI model for grading (default: from config)

    Returns:
        {
            "score": 85,
            "justification": "...",
            "grading_model": "gpt-4o-mini",
            "criteria_used": "..."
        }
    """
    if grading_model is None:
        grading_model = GRADING_MODEL

    if criteria is None:
        criteria = DEFAULT_SCORING_CRITERIA

    grading_prompt = f"""You are an expert evaluator of AI responses. Your task is to score the following response on a scale of 0-100.

Evaluation Criteria: {criteria}

Original Prompt:
{prompt}

Response to Evaluate:
{response}

Please provide:
1. A numerical score from 0-100 (use whole numbers or decimals like 85.5 if appropriate)
2. A brief justification (2-3 sentences) explaining your score

Format your response as:
SCORE: [number]
JUSTIFICATION: [your explanation]
"""

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=grading_model,
            messages=[{"role": "user", "content": grading_prompt}],
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
            "criteria_used": criteria,
        }

    except Exception as e:
        return {
            "score": None,
            "justification": f"Scoring failed: {str(e)}",
            "grading_model": grading_model,
            "criteria_used": criteria,
            "error": str(e),
        }


async def rank_responses(
    prompt: str, responses: Dict[str, str], criteria: Optional[str] = None
) -> Dict[str, int]:
    """
    Compare all 3 responses and rank them.

    Args:
        prompt: Original input prompt
        responses: {"openai": "...", "gemini": "...", "claude": "..."}
        criteria: Optional scoring criteria

    Returns:
        {
            "openai": 1,
            "gemini": 2,
            "claude": 3,
            "winner": "openai"
        }
    """
    if criteria is None:
        criteria = DEFAULT_SCORING_CRITERIA

    ranking_prompt = f"""You are comparing three different AI model responses to the same prompt. Rank them from 1 (best) to 3 (worst).

Evaluation Criteria: {criteria}

Original Prompt:
{prompt}

Response A (OpenAI):
{responses.get('openai', 'No response')}

Response B (Gemini):
{responses.get('gemini', 'No response')}

Response C (Claude):
{responses.get('claude', 'No response')}

Rank these responses from 1 (best) to 3 (worst) based on the criteria.

Format your response as:
OPENAI_RANK: [1, 2, or 3]
GEMINI_RANK: [1, 2, or 3]
CLAUDE_RANK: [1, 2, or 3]
WINNER: [openai, gemini, or claude]
"""

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=GRADING_MODEL,
            messages=[{"role": "user", "content": ranking_prompt}],
        )

        result_text = completion.choices[0].message.content

        openai_rank_match = re.search(
            r"OPENAI_RANK:\s*(\d)", result_text, re.IGNORECASE
        )
        gemini_rank_match = re.search(
            r"GEMINI_RANK:\s*(\d)", result_text, re.IGNORECASE
        )
        claude_rank_match = re.search(
            r"CLAUDE_RANK:\s*(\d)", result_text, re.IGNORECASE
        )
        winner_match = re.search(
            r"WINNER:\s*(openai|gemini|claude)", result_text, re.IGNORECASE
        )

        ranks = {
            "openai": int(openai_rank_match.group(1)) if openai_rank_match else 2,
            "gemini": int(gemini_rank_match.group(1)) if gemini_rank_match else 2,
            "claude": int(claude_rank_match.group(1)) if claude_rank_match else 2,
        }

        winner = (
            winner_match.group(1).lower() if winner_match else min(ranks, key=ranks.get)
        )
        ranks["winner"] = winner

        return ranks

    except Exception as e:
        return {
            "openai": 1,
            "gemini": 2,
            "claude": 3,
            "winner": "openai",
            "error": str(e),
        }


async def score_all_responses(
    prompt: str, responses: Dict[str, Dict], criteria: Optional[str] = None
) -> Dict:
    """
    Score all three LLM responses in parallel.

    Args:
        prompt: Original input prompt
        responses: {"openai": {...}, "gemini": {...}, "claude": {...}}
        criteria: Optional scoring criteria

    Returns:
        {
            "openai": {"score": 8.5, "justification": "...", "rank": 1},
            "gemini": {"score": 7.2, "justification": "...", "rank": 3},
            "claude": {"score": 8.0, "justification": "...", "rank": 2},
            "winner": "openai"
        }
    """
    response_texts = {
        "openai": responses.get("openai", {}).get("response", ""),
        "gemini": responses.get("gemini", {}).get("response", ""),
        "claude": responses.get("claude", {}).get("response", ""),
    }

    openai_score_task = score_response(prompt, response_texts["openai"], criteria)
    gemini_score_task = score_response(prompt, response_texts["gemini"], criteria)
    claude_score_task = score_response(prompt, response_texts["claude"], criteria)

    openai_score, gemini_score, claude_score = await asyncio.gather(
        openai_score_task, gemini_score_task, claude_score_task
    )

    model_scores = {
        "openai": openai_score.get("score", 0),
        "gemini": gemini_score.get("score", 0),
        "claude": claude_score.get("score", 0),
    }
    
    sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
    
    ranks = {}
    for rank, (model, score) in enumerate(sorted_models, start=1):
        ranks[model] = rank
    
    winner = sorted_models[0][0]

    result = {
        "openai": {**openai_score, "rank": ranks["openai"]},
        "gemini": {**gemini_score, "rank": ranks["gemini"]},
        "claude": {**claude_score, "rank": ranks["claude"]},
        "winner": winner,
    }

    return result
