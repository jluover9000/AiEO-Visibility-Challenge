from typing import List, Dict, Optional
import re
import os


def parse_uploaded_files(uploaded_files) -> List[Dict]:
    """
    Process uploaded .md files.
    
    Args:
        uploaded_files: Single file or list of files from Streamlit file_uploader
        
    Returns:
        List of dicts: [{"filename": "prompt1.md", "content": "..."}]
    """
    if uploaded_files is None:
        return []
    
    if not isinstance(uploaded_files, list):
        uploaded_files = [uploaded_files]
    
    parsed_files = []
    
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        
        if not filename.endswith('.md'):
            continue
        
        try:
            content = uploaded_file.read().decode('utf-8')
            parsed_files.append({
                "filename": filename,
                "content": content
            })
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
    
    return parsed_files


def validate_files(uploaded_files) -> bool:
    """
    Validate that uploaded files are .md files.
    
    Args:
        uploaded_files: Single file or list of files from Streamlit file_uploader
        
    Returns:
        True if all files are valid .md files, False otherwise
    """
    if uploaded_files is None:
        return False
    
    if not isinstance(uploaded_files, list):
        uploaded_files = [uploaded_files]
    
    for uploaded_file in uploaded_files:
        if not uploaded_file.name.endswith('.md'):
            return False
    
    return True


def extract_persona(prompt_content: str) -> Optional[str]:
    """
    Extract persona identifier from prompt header.

    Expected format:
    Persona: canadian_business_startup

    Args:
        prompt_content: The markdown prompt content

    Returns:
        Persona name (e.g., 'canadian_business_startup') or None if not found
    """
    if not prompt_content:
        return None

    pattern = r'^Persona:\s*(\w+)\s*$'

    for line in prompt_content.split('\n')[:10]:
        match = re.match(pattern, line.strip(), re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def load_persona(persona_name: str) -> Optional[str]:
    """
    Load persona content from personas/{persona_name}.md file.

    Args:
        persona_name: Name of the persona file (without .md extension)

    Returns:
        Full persona content or None if file doesn't exist
    """
    if not persona_name:
        return None

    personas_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "personas")
    persona_file = os.path.join(personas_dir, f"{persona_name}.md")

    try:
        with open(persona_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error loading persona {persona_name}: {e}")
        return None


def remove_persona_header(prompt_content: str) -> str:
    """
    Remove 'Persona: ...' line from prompt before sending to LLMs.

    Args:
        prompt_content: The full prompt text including persona header

    Returns:
        Clean prompt without persona header
    """
    if not prompt_content:
        return prompt_content

    lines = prompt_content.split('\n')
    clean_lines = [
        line for line in lines
        if not re.match(r'^Persona:\s*\w+\s*$', line.strip(), re.IGNORECASE)
    ]

    return '\n'.join(clean_lines).strip()


def extract_scoring_prompt_name(prompt_content: str) -> Optional[str]:
    """
    Extract scoring prompt identifier from the prompt header.

    Expected format:
    Scoring-Prompt: canadian_business_scoring

    Args:
        prompt_content: The markdown prompt content

    Returns:
        Scoring prompt name (e.g., 'canadian_business_scoring') or None if not found
    """
    if not prompt_content:
        return None

    pattern = r'^Scoring-Prompt:\s*(\w+)\s*$'

    for line in prompt_content.split('\n')[:10]:
        match = re.match(pattern, line.strip(), re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def load_scoring_prompt(scoring_prompt_name: str) -> Optional[str]:
    """
    Load scoring prompt content from scoring_prompts/{scoring_prompt_name}.md file.

    Args:
        scoring_prompt_name: Name of the scoring prompt file (without .md extension)

    Returns:
        Full scoring prompt content or None if file doesn't exist
    """
    if not scoring_prompt_name:
        return None

    scoring_prompts_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "scoring_prompts"
    )
    scoring_prompt_file = os.path.join(scoring_prompts_dir, f"{scoring_prompt_name}.md")

    try:
        with open(scoring_prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error loading scoring prompt {scoring_prompt_name}: {e}")
        return None


def remove_scoring_prompt_header(prompt_content: str) -> str:
    """
    Remove 'Scoring-Prompt: ...' line from prompt before sending to advisor LLMs.

    Args:
        prompt_content: The full prompt text including scoring-prompt header

    Returns:
        Clean prompt without scoring-prompt header
    """
    if not prompt_content:
        return prompt_content

    lines = prompt_content.split('\n')
    clean_lines = [
        line for line in lines
        if not re.match(r'^Scoring-Prompt:\s*\w+\s*$', line.strip(), re.IGNORECASE)
    ]

    return '\n'.join(clean_lines).strip()
