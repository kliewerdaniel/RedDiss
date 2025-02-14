from typing import Dict, Any, List
import json
import re
from pathlib import Path
from litellm import acompletion

class LyricsGenerator:
    def __init__(self):
        # Using ollama with litellm
        self.model = "ollama/llama3.3:latest"
    
    async def generate_lyrics(self, themes: Dict[str, Any], style: str) -> Dict[str, Any]:
        """
        Generate diss track lyrics based on extracted themes and style
        
        Args:
            themes (Dict[str, Any]): Extracted themes and context
            style (str): The style of the diss track
            
        Returns:
            Dict[str, Any]: Generated lyrics with structure
        """
        # Build context from themes
        context = self._build_context(themes, style)
        
        # Generate lyrics using ollama
        lyrics = await self._generate_verses(context)
        
        # Structure the lyrics
        structured_lyrics = self._structure_lyrics(lyrics)
        
        # Save generated lyrics
        Path("data/lyrics").mkdir(parents=True, exist_ok=True)
        safe_target = re.sub(r'[^a-zA-Z0-9_-]', '_', themes['target'])
        with open(f"data/lyrics/lyrics_{safe_target}.json", "w") as f:
            json.dump(structured_lyrics, f, indent=2)
        
        return structured_lyrics
    
    def _build_context(self, themes: Dict[str, Any], style: str) -> str:
        """Build context for lyrics generation"""
        # Extract main themes
        main_themes = [t["theme"] for t in themes["main_themes"]]
        
        # Build prompt
        prompt = f"""Generate a {style.lower()} diss track targeting {themes['target']} from r/{themes['context']}.
    Main themes to focus on: {', '.join(main_themes)}
    
    The track should:
1. Include clever wordplay and metaphors
2. Reference the target's background and context
3. Have a clear flow and rhythm
4. Include punchlines that hit hard
5. Maintain a consistent theme throughout

Structure:
- 16 bars for verse 1
- 8 bars for hook/chorus
- 16 bars for verse 2
- 8 bars for hook/chorus (repeat)
- 8 bars for outro

Each bar should have internal rhyme schemes and follow proper rap cadence."""
        
        return prompt
    
    async def _generate_verses(self, context: str) -> str:
        """Generate verses using ollama through litellm"""
        try:
            response = await acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a skilled battle rapper who excels at writing diss tracks."},
                    {"role": "user", "content": context}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating lyrics: {str(e)}")
            return ""
    
    def _structure_lyrics(self, raw_lyrics: str) -> Dict[str, Any]:
        """Structure raw lyrics into verses and chorus"""
        # Split lyrics into sections
        sections = raw_lyrics.split("\n\n")
        
        structured = {
            "verse1": sections[0] if len(sections) > 0 else "",
            "chorus": sections[1] if len(sections) > 1 else "",
            "verse2": sections[2] if len(sections) > 2 else "",
            "outro": sections[-1] if len(sections) > 3 else ""
        }
        
        return structured

# Initialize global generator
_generator = None

async def generate_lyrics(themes: Dict[str, Any], style: str) -> Dict[str, Any]:
    """Main function to generate lyrics"""
    global _generator
    if _generator is None:
        _generator = LyricsGenerator()
    return await _generator.generate_lyrics(themes, style)
