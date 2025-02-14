from typing import Dict, Any
import os
import json
import traceback
import numpy as np
from pathlib import Path
import soundfile as sf
import subprocess
import tempfile

class TTSEngine:
    def __init__(self):
        try:
            print("Initializing TTS Engine...")
            
            # Verify 'say' command is available (macOS)
            try:
                subprocess.run(['say', '-?'], capture_output=True)
            except FileNotFoundError:
                raise RuntimeError("macOS 'say' command not available")
                
            # Verify ffmpeg is available
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True)
            except FileNotFoundError:
                raise RuntimeError("ffmpeg not available")
            
            print("TTS engine initialized successfully")
            
        except Exception as e:
            error_msg = f"Error initializing TTS: {str(e)}"
            print(error_msg)
            print(f"Full error traceback:\n{traceback.format_exc()}")
            raise RuntimeError(error_msg)
    
    async def text_to_speech(self, lyrics: Dict[str, Any]) -> str:
        """
        Convert lyrics to speech using macOS say command with audio post-processing
        
        Args:
            lyrics (Dict[str, Any]): Lyrics structure
            
        Returns:
            str: Path to generated audio file
        """
        try:
            # Create output directory
            Path("data/audio").mkdir(parents=True, exist_ok=True)
            
            # Generate audio for each section
            audio_sections = []
            sample_rate = 44100  # Higher quality sample rate
            
            for section, content in lyrics.items():
                if content:
                    # Clean the content
                    clean_content = self._clean_content(content)
                    
                    # Generate audio using macOS 'say' command
                    with tempfile.NamedTemporaryFile(suffix='.aiff', delete=False) as temp_aiff:
                        # Create a temporary file for the text content
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_txt:
                            temp_txt.write(clean_content)
                            temp_txt.flush()
                            
                            try:
                                # Generate base audio with natural voice
                                subprocess.run([
                                    'say',
                                    '-v', 'Daniel',  # Daniel voice has good clarity
                                    '-r', '220',     # Faster speech rate for rap
                                    '-f', temp_txt.name,
                                    '-o', temp_aiff.name
                                ], check=True)
                                
                                # Process audio with ffmpeg for better quality
                                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                                    subprocess.run([
                                        'ffmpeg',
                                        '-i', temp_aiff.name,
                                        '-af', 'acompressor=threshold=-12dB:ratio=3:attack=0.1:release=0.2',  # Faster compression
                                        '-ar', str(sample_rate),  # Set sample rate
                                        '-ac', '1',              # Convert to mono
                                        '-y',                    # Overwrite output
                                        temp_wav.name
                                    ], check=True, capture_output=True)
                                    
                                    # Read processed audio
                                    audio_array, sr = sf.read(temp_wav.name)
                                    
                                    # Normalize audio
                                    audio_array = audio_array / np.max(np.abs(audio_array))
                                    
                                    audio_sections.append(audio_array)
                                    
                                    os.unlink(temp_wav.name)
                                    
                            finally:
                                os.unlink(temp_txt.name)
                                os.unlink(temp_aiff.name)
                    
                    # Add shorter pause between sections
                    pause = np.zeros(int(sample_rate * 0.3))  # 0.3 second pause
                    audio_sections.append(pause)
            
            # Combine all sections
            final_audio = np.concatenate(audio_sections)
            
            # Save final audio
            output_path = "data/audio/raw_vocals.wav"
            sf.write(output_path, final_audio, sample_rate)
            
            # Save generation metadata
            metadata = {
                "sample_rate": sample_rate,
                "duration": len(final_audio) / sample_rate,
                "sections": list(lyrics.keys())
            }
            
            with open("data/audio/vocals_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            return output_path
            
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            print(f"Full error traceback:\n{traceback.format_exc()}")
            raise RuntimeError(f"Failed to generate audio: {str(e)}")
    
    def _clean_content(self, content: str) -> str:
        """Clean content by removing tags and normalizing text"""
        # Remove any XML-like tags
        import re
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # Normalize whitespace
        clean_content = ' '.join(clean_content.split())
        
        # Add periods for natural pauses if missing
        if not clean_content.endswith(('.', '!', '?')):
            clean_content += '.'
            
        return clean_content.strip()

# Initialize global TTS engine
_tts_engine = None

async def text_to_speech(lyrics: Dict[str, Any]) -> str:
    """Main function to convert lyrics to speech"""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine()
    return await _tts_engine.text_to_speech(lyrics)
