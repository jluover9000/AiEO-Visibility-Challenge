from typing import List, Dict, Optional
import re


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


def extract_scoring_criteria(prompt_content: str) -> Optional[str]:
    """
    Extract scoring criteria from an explicit scoring block.
    
    Expected format:
    --- SCORING CRITERIA ---
    Your evaluation criteria here
    --- END SCORING CRITERIA ---
    
    Args:
        prompt_content: The markdown prompt content
        
    Returns:
        Criteria string or None if no criteria block found
    """
    if not prompt_content:
        return None
    
    pattern = r'---\s*SCORING CRITERIA\s*---\s*(.+?)\s*---\s*END SCORING CRITERIA\s*---'
    match = re.search(pattern, prompt_content, re.IGNORECASE | re.DOTALL)
    
    if match:
        criteria = match.group(1).strip()
        return criteria
    
    return None


def remove_scoring_criteria(prompt_content: str) -> str:
    """
    Remove the explicit scoring block from the prompt before sending to LLMs.
    
    Removes:
    --- SCORING CRITERIA ---
    Your evaluation criteria here
    --- END SCORING CRITERIA ---
    
    Args:
        prompt_content: The full prompt text including scoring block
        
    Returns:
        Clean prompt without scoring block
    """
    if not prompt_content:
        return prompt_content
    
    pattern = r'---\s*SCORING CRITERIA\s*---\s*.+?\s*---\s*END SCORING CRITERIA\s*---\s*'
    clean_prompt = re.sub(pattern, '', prompt_content, flags=re.IGNORECASE | re.DOTALL)
    
    return clean_prompt.strip()
