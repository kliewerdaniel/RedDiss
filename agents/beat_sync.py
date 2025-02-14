from typing import Dict, Any
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import json
import aiohttp
import tempfile

class BeatSynchronizer:
    def __init__(self):
        self.target_tempo = 90  # Default target tempo (BPM)
    
    async def sync_to_beat(self, vocals_path: str, beat_url: str) -> str:
        """
        Synchronize vocals with a beat
        
        Args:
            vocals_path (str): Path to the raw vocals WAV file
            beat_url (str): URL to download the beat file
            
        Returns:
            str: Path to synchronized audio file
        """
        try:
            # Load vocals
            vocals, vocals_sr = librosa.load(vocals_path)
            
            # Download and load beat
            beat_path = await self._download_beat(beat_url)
            beat, beat_sr = librosa.load(beat_path)
            
            # Analyze beat
            beat_tempo, beat_frames = librosa.beat.beat_track(y=beat, sr=beat_sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=beat_sr)
            
            # Time-stretch vocals to match beat tempo
            stretched_vocals = self._time_stretch_to_tempo(
                vocals, vocals_sr, beat_tempo
            )
            
            # Align vocals with beat grid
            aligned_vocals = self._align_to_grid(
                stretched_vocals, vocals_sr, beat_times
            )
            
            # Mix vocals with beat
            mixed_audio = self._mix_audio(aligned_vocals, beat)
            
            # Save final mix
            output_path = "data/audio/synced_track.wav"
            sf.write(output_path, mixed_audio, beat_sr)
            
            # Save sync metadata
            metadata = {
                "beat_tempo": float(beat_tempo),
                "original_vocal_duration": len(vocals) / vocals_sr,
                "final_duration": len(mixed_audio) / beat_sr,
                "beat_url": beat_url
            }
            
            with open("data/audio/sync_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            return output_path
            
        except Exception as e:
            print(f"Error syncing audio: {str(e)}")
            return vocals_path  # Return original vocals if sync fails
    
    async def _download_beat(self, url: str) -> str:
        """Download beat file from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    # Create temp file
                    temp_file = tempfile.NamedTemporaryFile(
                        suffix=".mp3", delete=False
                    )
                    temp_file.write(await response.read())
                    return temp_file.name
                else:
                    raise Exception(f"Failed to download beat: {response.status}")
    
    def _time_stretch_to_tempo(
        self, audio: np.ndarray, sr: int, target_tempo: float
    ) -> np.ndarray:
        """Time-stretch audio to match target tempo"""
        # Estimate original tempo
        original_tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        
        if original_tempo > 0:
            # Calculate stretch factor
            stretch_factor = original_tempo / target_tempo
            # Time-stretch audio
            stretched = librosa.effects.time_stretch(audio, rate=stretch_factor)
            return stretched
        
        return audio
    
    def _align_to_grid(
        self, audio: np.ndarray, sr: int, beat_times: np.ndarray
    ) -> np.ndarray:
        """Align audio to beat grid"""
        # Find onset strength
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        
        # Find onset frames
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env, sr=sr
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
        # Create output buffer
        out_audio = np.zeros_like(audio)
        
        # For each onset, find nearest beat and align
        for onset_time in onset_times:
            nearest_beat = beat_times[
                np.argmin(np.abs(beat_times - onset_time))
            ]
            time_diff = nearest_beat - onset_time
            
            # Shift audio segment
            if time_diff > 0:
                shift_samples = int(time_diff * sr)
                out_audio[shift_samples:] = audio[:-shift_samples]
            else:
                shift_samples = int(-time_diff * sr)
                out_audio[:-shift_samples] = audio[shift_samples:]
        
        return out_audio
    
    def _mix_audio(
        self, vocals: np.ndarray, beat: np.ndarray, vocals_gain: float = 0.8
    ) -> np.ndarray:
        """Mix vocals with beat"""
        # Ensure same length
        max_len = max(len(vocals), len(beat))
        if len(vocals) < max_len:
            vocals = np.pad(vocals, (0, max_len - len(vocals)))
        if len(beat) < max_len:
            beat = np.pad(beat, (0, max_len - len(beat)))
        
        # Mix with vocals slightly louder than beat
        mixed = (vocals * vocals_gain + beat * 0.6)
        
        # Normalize
        mixed = mixed / np.max(np.abs(mixed))
        
        return mixed

# Initialize global synchronizer
_synchronizer = None

async def sync_to_beat(vocals_path: str, beat_url: str) -> str:
    """Main function to synchronize audio"""
    global _synchronizer
    if _synchronizer is None:
        _synchronizer = BeatSynchronizer()
    return await _synchronizer.sync_to_beat(vocals_path, beat_url)
