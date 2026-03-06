# Changelog

## Version 2.0.0 - Inspect-AI Scoring Integration (2026-02-26)

### New Features

#### Automatic Response Scoring
- Integrated model-graded evaluation using OpenAI's gpt-4o-mini
- Automatic scoring after all three LLM responses complete
- Scores on 0-100 scale with detailed justifications

#### Response Ranking
- Comparative ranking of all three responses (1st, 2nd, 3rd place)
- Automatic winner identification based on scores
- Winner highlighted in green in comparison table

#### Flexible Scoring Criteria
- Parse scoring instructions from .md prompt files
- Support multiple formats: explicit blocks, natural language
- Fallback to default criteria if none specified

#### Enhanced UI
- Score comparison table with Model, Score, and Rank columns
- Winner display with trophy emoji and score
- Expandable justifications for each model's score
- Visual highlighting of winning response

#### Enhanced JSON Logs
- Scores included in downloadable logs
- Ranks and justifications for each response
- Scoring criteria used for evaluation
- Winner information

### New Files

- `services/scoring_service.py` - Core scoring logic with three functions:
  - `score_response()` - Score individual response
  - `rank_responses()` - Comparative ranking
  - `score_all_responses()` - Parallel scoring orchestrator
- `test_prompts/sample_prompt_with_scoring.md` - Example with explicit criteria
- `test_prompts/sample_prompt_technical.md` - Example with natural language criteria
- `SCORING_GUIDE.md` - Complete documentation for scoring features

### Modified Files

- `requirements.txt` - Added pandas for table display
- `config.py` - Added GRADING_MODEL and DEFAULT_SCORING_CRITERIA
- `services/file_handler.py` - Added extract_scoring_criteria() function
- `app.py` - Integrated scoring after LLM responses, added comparison table and winner display

### Dependencies Added

- `pandas` - For DataFrame display in Streamlit

### Cost Impact

- Scoring cost: ~$0.0012 per prompt (negligible, <1% of total)
- Uses gpt-4o-mini for cost-effective evaluation

---

## Version 1.0.0 - Initial Release (2026-02-26)

### Features

- Multi-LLM support (OpenAI, Gemini, Claude)
- Real-time streaming responses
- Parallel processing of all three LLMs
- Password authentication
- File upload (.md files, single or multiple)
- Three-column side-by-side display
- JSON log generation and download
- S3 upload support (optional)
- Complete AWS deployment guide

### Project Structure

- Streamlit-based web application
- Modular service architecture
- Environment-based configuration
- Comprehensive documentation
