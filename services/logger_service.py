import json
from datetime import datetime, timezone
from typing import Dict, Optional
from botocore.exceptions import ClientError, NoCredentialsError


def format_log_data(results: Dict) -> str:
    """
    Format results data as pretty-printed JSON string.

    Args:
        results: Dictionary containing session data and responses

    Returns:
        JSON string formatted for readability
    """
    return json.dumps(results, indent=2, ensure_ascii=False)


def save_log_locally(results: Dict) -> str:
    """
    Save log data to a local JSON file.

    Args:
        results: Dictionary containing session data and responses

    Returns:
        Local file path
    """
    session_id = results.get(
        "session_id", datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    )
    filename = f"llm_logs_{session_id}.json"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(format_log_data(results))

    return filename


def create_downloadable_json(results: Dict) -> bytes:
    """
    Create downloadable JSON bytes for Streamlit download button.

    Args:
        results: Dictionary containing session data and responses

    Returns:
        JSON data as bytes
    """
    return format_log_data(results).encode("utf-8")
