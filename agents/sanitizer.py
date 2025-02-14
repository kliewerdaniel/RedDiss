from typing import Dict, Any
import re
import json
from pathlib import Path

async def clean_text(content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and preprocess Reddit content
    
    Args:
        content (Dict[str, Any]): Raw Reddit content
        
    Returns:
        Dict[str, Any]: Cleaned and preprocessed content
    """
    print("Starting text cleaning process...")
    print(f"Input content keys: {content.keys()}")
    
    cleaned_data = {
        "title": _clean_string(content["title"]),
        "main_text": _clean_string(content["selftext"]),
        "author": content["author"],
        "subreddit": content["subreddit"],
        "comments": []
    }
    
    # Clean comment text
    for comment in content["comments"]:
        if comment["score"] > 0:  # Filter out downvoted comments
            cleaned_data["comments"].append({
                "text": _clean_string(comment["body"]),
                "author": comment["author"],
                "score": comment["score"]
            })
    
    # Sort comments by score
    cleaned_data["comments"] = sorted(
        cleaned_data["comments"],
        key=lambda x: x["score"],
        reverse=True
    )
    
    # Save processed data
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename
    safe_author = re.sub(r'[^a-zA-Z0-9_-]', '_', content['author'])
    output_path = f"data/processed/cleaned_{safe_author}.json"
    
    print(f"Saving cleaned data to: {output_path}")
    print(f"Cleaned content structure: {list(cleaned_data.keys())}")
    print(f"Number of processed comments: {len(cleaned_data['comments'])}")
    
    with open(output_path, "w") as f:
        json.dump(cleaned_data, f, indent=2)
    
    return cleaned_data

def _clean_string(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
        
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove Reddit-style formatting and HTML entities
    text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
    text = re.sub(r'&(?:amp|lt|gt|#\d+|[a-zA-Z]+);', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^a-z0-9\s.,!?\'"-]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove repeated punctuation
    text = re.sub(r'([.,!?])\1+', r'\1', text)
    
    return text
