from typing import Dict, Any
import json
from pathlib import Path
from litellm import acompletion

class FlowRefiner:
    def __init__(self):
        # Using ollama with litellm
        self.model = "ollama/llama3.3:latest"
    
    async def refine_flow(self, lyrics: Dict[str, Any], flow_complexity: int) -> Dict[str, Any]:
        """
        Enhance flow and punchlines in generated lyrics
        
        Args:
            lyrics (Dict[str, Any]): Generated lyrics structure
            
        Returns:
            Dict[str, Any]: Refined lyrics with enhanced flow
        """
        refined_lyrics = {}
        
        # Refine each section
        for section, content in lyrics.items():
            refined_lyrics[section] = await self._enhance_section(content, section, flow_complexity)
        
        # Save refined lyrics
        Path("data/refined").mkdir(parents=True, exist_ok=True)
        with open(f"data/refined/refined_lyrics.json", "w") as f:
            json.dump(refined_lyrics, f, indent=2)
        
        return refined_lyrics
    
    async def _enhance_section(self, content: str, section_type: str, flow_complexity: int) -> str:
        """Enhance a specific section of lyrics"""
        if not content:
            return ""
            
        prompt = self._build_enhancement_prompt(content, section_type)
        
        try:
            response = await acompletion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a master battle rapper focused on improving flow and punchlines while maintaining the original message. Output only the enhanced lyrics without any tags, directions, or explanations."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Clean the response to remove any tags or directions
            enhanced_lyrics = self._clean_response(response.choices[0].message.content.strip())
            return enhanced_lyrics
            
        except Exception as e:
            print(f"Error refining flow: {str(e)}")
            return content
    
    def _build_enhancement_prompt(self, content: str, section_type: str) -> str:
        """Build prompt for flow enhancement"""
        return f"""Enhance the following {section_type} while maintaining its core message and theme.
Focus on:
1. Tightening internal rhyme schemes
2. Adding clever wordplay and double entendres
3. Strengthening punchlines
4. Improving flow and rhythm
5. Maintaining consistent syllable patterns

Original content:
{content}

Provide ONLY the enhanced lyrics without any tags, directions, or explanations. Do not include any [pause], [emph], [speed], or other markers. Do not include any explanations of changes made."""

    def _clean_response(self, response: str) -> str:
        """Clean the response to remove any tags or directions"""
        import re
        
        # Remove any lines starting with common direction words
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        filtered_lines = [
            line for line in lines 
            if not line.lower().startswith(('here', 'enhanced', 'original', 'verse', 'chorus', 'improved', 'note', 'adding'))
        ]
        
        # Remove any markdown or other formatting
        cleaned = '\n'.join(filtered_lines)
        cleaned = re.sub(r'[*_~`]', '', cleaned)  # Remove markdown
        cleaned = re.sub(r'\[.*?\]', '', cleaned)  # Remove square bracket tags
        cleaned = re.sub(r'<.*?>', '', cleaned)   # Remove angle bracket tags
        
        # Remove any remaining directional text
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)  # Remove parenthetical directions
        
        # Clean up extra whitespace
        cleaned = '\n'.join(line.strip() for line in cleaned.split('\n') if line.strip())
        
        return cleaned

# Initialize global refiner
_refiner = None

async def refine_flow(lyrics: Dict[str, Any], flow_complexity: int) -> Dict[str, Any]:
    """Main function to refine lyrics flow"""
    global _refiner
    if _refiner is None:
        _refiner = FlowRefiner()
    return await _refiner.refine_flow(lyrics, flow_complexity)
