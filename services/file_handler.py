from typing import List, Dict


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
