import json
import boto3
from datetime import datetime
from typing import Dict, Optional
from botocore.exceptions import ClientError, NoCredentialsError

from config import S3_BUCKET_NAME, AWS_REGION


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
    session_id = results.get("session_id", datetime.utcnow().strftime("%Y%m%d_%H%M%S"))
    filename = f"llm_logs_{session_id}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(format_log_data(results))
    
    return filename


def upload_to_s3(results: Dict, bucket_name: Optional[str] = None) -> Dict[str, str]:
    """
    Upload JSON log to S3 bucket.
    
    Args:
        results: Dictionary containing session data and responses
        bucket_name: S3 bucket name (defaults to config value)
        
    Returns:
        Dict with 'status', 'message', and optionally 'url' or 'local_path'
    """
    if bucket_name is None:
        bucket_name = S3_BUCKET_NAME
    
    if not bucket_name:
        local_path = save_log_locally(results)
        return {
            "status": "local",
            "message": "S3 bucket not configured. Log saved locally.",
            "local_path": local_path
        }
    
    session_id = results.get("session_id", datetime.utcnow().strftime("%Y%m%d_%H%M%S"))
    filename = f"llm_logs_{session_id}.json"
    
    try:
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        
        log_data = format_log_data(results)
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=log_data.encode('utf-8'),
            ContentType='application/json'
        )
        
        s3_url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        
        local_path = save_log_locally(results)
        
        return {
            "status": "success",
            "message": f"Log uploaded to S3 and saved locally",
            "s3_url": s3_url,
            "local_path": local_path,
            "filename": filename
        }
        
    except NoCredentialsError:
        local_path = save_log_locally(results)
        return {
            "status": "error",
            "message": "AWS credentials not found. Log saved locally.",
            "local_path": local_path
        }
        
    except ClientError as e:
        local_path = save_log_locally(results)
        return {
            "status": "error",
            "message": f"S3 upload failed: {str(e)}. Log saved locally.",
            "local_path": local_path
        }
        
    except Exception as e:
        local_path = save_log_locally(results)
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}. Log saved locally.",
            "local_path": local_path
        }


def create_downloadable_json(results: Dict) -> bytes:
    """
    Create downloadable JSON bytes for Streamlit download button.
    
    Args:
        results: Dictionary containing session data and responses
        
    Returns:
        JSON data as bytes
    """
    return format_log_data(results).encode('utf-8')
