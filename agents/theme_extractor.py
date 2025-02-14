from typing import Dict, Any, List
import json
import re
from pathlib import Path
from transformers import pipeline
import torch

class ThemeExtractor:
    def __init__(self):
        # Load zero-shot classification pipeline
        # Force CPU usage for consistency
        print("Initializing theme extractor on CPU...")
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1  # Force CPU usage
        )
        print("Theme extractor initialized successfully")
        
        # Common themes in diss tracks
        self.candidate_themes = [
            "wealth/money",
            "success/achievements",
            "skills/talent",
            "authenticity/realness",
            "street credibility",
            "relationships/loyalty",
            "competition/rivalry",
            "past conflicts",
            "personal style",
            "geographic location"
        ]
    
    async def extract_themes(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract main themes from cleaned Reddit content
        
        Args:
            content (Dict[str, Any]): Cleaned Reddit content
            
        Returns:
            Dict[str, Any]: Extracted themes and their relevance scores
        """
        # Combine title and main text
        main_content = f"{content['title']} {content['main_text']}"
        
        # Extract themes from main content
        main_themes = await self._classify_text(main_content)
        
        # Extract themes from top comments
        comment_themes = []
        for comment in content["comments"][:5]:  # Process top 5 comments
            themes = await self._classify_text(comment["text"])
            comment_themes.append({
                "author": comment["author"],
                "themes": themes
            })
        
        themes_data = {
            "main_themes": main_themes,
            "comment_themes": comment_themes,
            "target": content["author"],
            "context": content["subreddit"]
        }
        
        # Save extracted themes
        Path("data/themes").mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        safe_author = re.sub(r'[^a-zA-Z0-9_-]', '_', content['author'])
        with open(f"data/themes/themes_{safe_author}.json", "w") as f:
            json.dump(themes_data, f, indent=2)
        
        return themes_data
    
    async def _classify_text(self, text: str) -> List[Dict[str, float]]:
        """Classify text against candidate themes"""
        if not text.strip():
            return []
            
        result = self.classifier(
            text,
            candidate_labels=self.candidate_themes,
            multi_label=True
        )
        
        # Filter themes with confidence > 0.3
        themes = [
            {"theme": label, "confidence": score}
            for label, score in zip(result["labels"], result["scores"])
            if score > 0.3
        ]
        
        return sorted(themes, key=lambda x: x["confidence"], reverse=True)

# Initialize global extractor
_extractor = None

async def extract_themes(content: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to extract themes from content"""
    global _extractor
    if _extractor is None:
        _extractor = ThemeExtractor()
    return await _extractor.extract_themes(content)
