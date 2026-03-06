# Inspect-AI Scoring Integration Guide

## Overview

The Multi-LLM Prompt Tester now includes automatic scoring and ranking of responses from OpenAI, Gemini, and Claude using model-graded evaluation.

## How It Works

1. **Upload .md files** - Your prompts are sent to all three LLMs
2. **Responses stream in** - Real-time display in three columns
3. **Automatic scoring** - After all responses complete, a grading model (gpt-5-mini) evaluates each response
4. **Ranking** - Responses are automatically ranked based on their numerical scores (highest = #1)
5. **Display** - Scores shown in a comparison table with winner highlighted
6. **JSON log** - Scores, ranks, and justifications included in downloadable logs

## Adding Scoring Criteria to Your Prompts

### Explicit Scoring Block (Required Format)

To include scoring criteria, add a clearly delimited block at the end of your prompt:

```markdown
# Your Prompt Title

Your actual prompt content here...
Ask questions, give instructions, etc.

--- SCORING CRITERIA ---
Evaluate for creativity, technical accuracy, and clarity.
--- END SCORING CRITERIA ---
```

**Important:**
- The scoring block must use exactly this format with the three-dash delimiters
- The scoring criteria will be extracted and used for evaluation
- The scoring block will be removed before sending the prompt to LLMs
- This ensures LLMs don't see the judging instructions

### Default Criteria

If no explicit criteria is found in your prompt, the system uses:
> "Evaluate the response for accuracy, relevance, and helpfulness on a 0-100 scale."

## Using Personas

### What are Personas?

Personas are specialized roles that shape how LLMs respond. When you specify a persona, all three LLMs receive it as a system message, changing their behavior, tone, and expertise.

### Available Personas

- **canadian_business_startup**: Expert business advisor for starting businesses in Canada
- **educational_counselor**: Canadian education and scholarship advisor for students

### Adding Persona to Your Prompt

Add a persona header at the start of your prompt:

```markdown
Persona: canadian_business_startup

Your actual prompt here...

--- SCORING CRITERIA ---
Your scoring criteria here...
--- END SCORING CRITERIA ---
```

### Persona Format

```
Persona: <persona_name>
```

The persona name should match a file in the `personas/` directory (without the .md extension).

### How Personas Affect Scoring

When a persona is used:
- The scoring agent receives the persona context
- Evaluation includes whether the response aligns with the persona's role and expertise
- Scores consider both the criteria AND persona adherence

### Example with Persona

```markdown
Persona: educational_counselor

I want to study computer science in Canada. What universities should I consider?

--- SCORING CRITERIA ---
Evaluate for accuracy of program information and helpfulness for students.
--- END SCORING CRITERIA ---
```

The LLMs will respond as an educational counselor, and scoring will verify they maintained that role appropriately.

## Scoring Output

### Comparison Table

After all responses complete, you'll see a table like:

| Model  | Score | Rank |
|--------|-------|------|
| OpenAI | 85    | #1   |
| Gemini | 72    | #3   |
| Claude | 80    | #2   |

The winner row is highlighted in green.

### Winner Display

```
Winner: OPENAI with score 85/100
```

### Justifications

Expand each model's section to see detailed justification:

```
OPENAI - Score: 85/100, Rank: #1
▼ Highly creative narrative with vivid imagery and strong character development.
  The story has a clear arc and emotional depth. Minor room for improvement in pacing.
```

## JSON Log Format

Enhanced logs now include scoring data:

```json
{
  "session_id": "20260226_143000",
  "timestamp": "2026-02-26T14:30:00Z",
  "prompts": [
    {
      "filename": "creative_prompt.md",
      "content": "Write a story...\nScoring: Evaluate for creativity",
      "responses": {
        "openai": {
          "model": "gpt-4o-mini",
          "response": "Once upon a time...",
          "duration_seconds": 3.5,
          "timestamp": "2026-02-26T14:30:05Z",
          "error": null,
          "score": 85,
          "rank": 1,
          "justification": "Highly creative narrative..."
        },
        "gemini": { ... },
        "claude": { ... }
      },
      "winner": "openai",
      "scoring_criteria": "Evaluate for creativity"
    }
  ]
}
```

## Sample Test Files

### With Explicit Criteria

**test_prompts/sample_prompt_with_scoring.md:**
- Creative writing prompt
- Explicit scoring instructions for creativity, emotion, and structure

**test_prompts/sample_prompt_technical.md:**
- Technical explanation prompt
- Natural language scoring for accuracy and clarity

### Without Criteria (Uses Defaults)

**test_prompts/sample_prompt_1.md:**
- Creative writing without explicit scoring
- Uses default criteria

**test_prompts/sample_prompt_2.md:**
- Technical explanation without explicit scoring
- Uses default criteria

## Cost Impact

### Grading Model

Currently using: **gpt-5-mini**

- **Input pricing:** ~$0.15 per 1M tokens
- **Output pricing:** ~$0.60 per 1M tokens
- **Per score:** ~500 tokens total (~$0.0003)
- **Per prompt:** 3 scores + 1 ranking = ~$0.0012
- **Very affordable:** 1000 prompts ≈ $1.20

### Total Cost Per Prompt

- 3 LLM responses: $0.05-0.30 (varies by model)
- Scoring: $0.0012
- **Scoring adds < 1% to total cost**

## Error Handling

### Graceful Degradation

If scoring fails:
- ✅ LLM responses still displayed normally
- ✅ JSON download still works
- ⚠️ Scoring section shows error message
- ✅ Responses logged without scores

### Partial Failures

If one score fails:
- ✅ Other scores continue
- ⚠️ Failed score shows "N/A"
- ✅ Ranking still attempted with available scores

## Configuration

### Environment Variables

Add to your `.env.local` or Streamlit Cloud secrets:

```env
GRADING_MODEL=gpt-5-mini
DEFAULT_SCORING_CRITERIA="Evaluate the response for accuracy, relevance, and helpfulness on a 0-100 scale."
```

### Change Grading Model

You can use different models for grading:
- `gpt-5-mini` - Latest efficient model (default)
- `gpt-4o-mini` - Fast and cost-effective
- `gpt-4o` - More thorough, higher cost

## Testing Checklist

- [ ] Upload prompt without scoring criteria (uses defaults)
- [ ] Upload prompt with explicit scoring instructions
- [ ] Upload prompt without persona (default behavior)
- [ ] Upload prompt with canadian_business_startup persona
- [ ] Upload prompt with educational_counselor persona
- [ ] Verify all three responses get scored
- [ ] Check comparison table displays correctly
- [ ] Verify winner is highlighted in green
- [ ] Expand justification sections
- [ ] Download JSON and verify scores, personas are included
- [ ] Test with multiple prompts in one session
- [ ] Verify scoring criteria is parsed correctly
- [ ] Verify persona is applied correctly (check response content)
- [ ] Check error handling (disconnect network during scoring)

## Troubleshooting

### "Scoring failed" error

**Possible causes:**
1. OPENAI_API_KEY not set or invalid
2. GRADING_MODEL not supported
3. Network connectivity issues
4. Rate limiting from OpenAI API

**Solutions:**
- Check API key in environment/secrets
- Verify grading model name is correct
- Wait and retry if rate limited

### Scores show as "N/A"

**Causes:**
- Scoring API call failed for that specific model
- Response was empty or had error

**Solution:**
- Check individual justifications for error details
- Response will still be downloadable

### Incorrect parsing of criteria

**Causes:**
- Criteria not using the required block format
- Missing delimiters

**Solution:**
- Use the exact format with three-dash delimiters
- Must have both start and end markers
- Place scoring block at the end of your prompt

## Future Enhancements

Potential improvements:
1. Multiple dimension scoring (accuracy, creativity, style separately)
2. Custom scoring models per prompt
3. User-selectable grading model in UI
4. Confidence scores for rankings
5. Historical comparison across sessions
6. Export scores to CSV for analysis

---

**Ready to use!** Upload prompts with or without explicit scoring criteria and see automatic evaluation of all three LLM responses.
