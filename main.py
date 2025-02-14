from fastapi import FastAPI, HTTPException
from typing import Optional
from pathlib import Path
import os
from dotenv import load_dotenv
from agents import (
    scraper,
    sanitizer,
    theme_extractor,
    lyrics_generator,
    flow_refiner,
    tts_engine,
    beat_sync,
    mastering
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Diss Track AI",
    description="AI-powered diss track generator using Reddit content",
    version="1.0.0"
)

# Ensure data directories exist
Path("data").mkdir(exist_ok=True)
Path("models").mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Diss Track AI Generator API"}

@app.get("/generate_diss")
async def generate_diss(url: str, style: str, beat_url: Optional[str] = None, flow_complexity: int = 5):
    """
    Generate a diss track from a Reddit post/comment
    
    Args:
        url (str): Reddit post/comment URL
        style (str): The style of the diss track (e.g., Aggressive, Playful, Sarcastic)
        beat_url (Optional[str]): URL to a beat file (optional)
    
    Returns:
        dict: Generated diss track information and file paths
    """
    try:
        # 1. Scrape Reddit content
        content = await scraper.scrape_reddit(url)
        
        # 2. Sanitize and preprocess text
        cleaned_text = await sanitizer.clean_text(content)
        
        # 3. Extract themes and topics
        themes = await theme_extractor.extract_themes(cleaned_text)
        
        # 4. Generate lyrics
        lyrics = await lyrics_generator.generate_lyrics(themes, style)

        # 5. Refine flow and punchlines
        refined_lyrics = await flow_refiner.refine_flow(lyrics, flow_complexity)
        
        # 6. Convert to speech
        speech_file = await tts_engine.text_to_speech(refined_lyrics)
        
        # 7. Sync with beat
        if beat_url:
            synced_audio = await beat_sync.sync_to_beat(speech_file, beat_url)
        else:
            synced_audio = speech_file
        
        # 8. Master final audio
        final_track = await mastering.master_audio(synced_audio)
        
        return {
            "status": "success",
            "lyrics": refined_lyrics,
            "audio_file": final_track
        }
        
    except HTTPException as e:
        # Re-raise existing HTTP exceptions
        raise e
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "step": "unknown"
        }
        
        # Determine which step failed
        error_lower = str(e).lower()
        if "asyncpraw" in error_lower or "reddit" in error_lower:
            error_detail["step"] = "reddit_scraping"
        elif "sanitizer" in error_lower:
            error_detail["step"] = "text_cleaning"
        elif "theme" in error_lower:
            error_detail["step"] = "theme_extraction"
        elif "lyrics" in error_lower:
            error_detail["step"] = "lyrics_generation"
        elif "flow" in error_lower:
            error_detail["step"] = "flow_refinement"
        elif "speech" in error_lower or "tts" in error_lower:
            error_detail["step"] = "text_to_speech"
        elif "beat" in error_lower or "sync" in error_lower:
            error_detail["step"] = "beat_syncing"
        elif "master" in error_lower or "audio" in error_lower:
            error_detail["step"] = "audio_mastering"
                
        print("Error details:", error_detail)  # Log error details
        raise HTTPException(status_code=500, detail=error_detail)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
