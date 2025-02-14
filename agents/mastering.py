from typing import Dict, Any
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import json
import traceback

class AudioMaster:
    def __init__(self):
        self.target_lufs = -14.0  # Standard streaming loudness
        self.target_peak = -1.0   # Peak level in dB
    
    async def master_audio(self, audio_path: str) -> str:
        """
        Master the final audio track
        
        Args:
            audio_path (str): Path to the synced audio file
            
        Returns:
            str: Path to mastered audio file
        """
        try:
            # Load audio using soundfile instead of librosa
            audio, sr = sf.read(audio_path)
            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            
            # Apply processing chain
            processed = audio
            
            # 1. Dynamic range compression
            processed = self._apply_compression(processed)
            
            # 2. EQ enhancement
            processed = self._apply_eq(processed, sr)
            
            # 3. Stereo enhancement
            processed = self._enhance_stereo(processed)
            
            # 4. Limiting and normalization
            processed = self._apply_limiting(processed)
            
            # Create output directory
            Path("data/audio/mastered").mkdir(parents=True, exist_ok=True)
            
            # Save mastered audio
            output_path = "data/audio/mastered/final_track.wav"
            try:
                # Ensure proper shape for stereo output
                if isinstance(processed, np.ndarray):
                    if processed.ndim == 2 and processed.shape[0] == 2:
                        # Already in correct shape (2, samples)
                        pass
                    elif processed.ndim == 2 and processed.shape[1] == 2:
                        # Convert from (samples, 2) to (2, samples)
                        processed = processed.T
                    elif processed.ndim == 1:
                        # Convert mono to stereo
                        processed = np.vstack((processed, processed))
                    
                    # Write audio file
                    sf.write(output_path, processed.T, sr)
                else:
                    print(f"Warning: Unexpected audio format: {type(processed)}")
                    return audio_path
            except Exception as write_error:
                print(f"Error writing audio file: {str(write_error)}")
                print(f"Error details: {traceback.format_exc()}")
                return audio_path
            
            # Calculate and save mastering metadata
            metadata = self._calculate_audio_metrics(processed, sr)
            
            with open("data/audio/mastered/mastering_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            return output_path
            
        except Exception as e:
            print(f"Error mastering audio: {str(e)}")
            print(f"Error details: {traceback.format_exc()}")
            return audio_path  # Return original audio if mastering fails
    
    def _apply_compression(self, audio: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression"""
        # Calculate RMS energy
        rms = librosa.feature.rms(y=audio)[0]
        
        # Set compression parameters
        threshold = np.mean(rms) * 1.5
        ratio = 4.0
        attack = 0.003
        release = 0.1
        
        # Apply compression
        compressed = np.zeros_like(audio)
        gain = np.ones_like(audio)
        
        for i in range(len(audio)):
            if abs(audio[i]) > threshold:
                gain[i] = threshold + (abs(audio[i]) - threshold) / ratio
                gain[i] /= abs(audio[i])
            
            # Apply attack/release
            if i > 0:
                if gain[i] < gain[i-1]:
                    gain[i] = gain[i-1] + (gain[i] - gain[i-1]) * attack
                else:
                    gain[i] = gain[i-1] + (gain[i] - gain[i-1]) * release
            
            compressed[i] = audio[i] * gain[i]
        
        return compressed
    
    def _apply_eq(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply equalizer enhancement"""
        # Convert to frequency domain
        D = librosa.stft(audio)
        
        # Define frequency bands
        bands = {
            "sub_bass": (20, 60),
            "bass": (60, 250),
            "low_mids": (250, 2000),
            "high_mids": (2000, 6000),
            "highs": (6000, sr//2)
        }
        
        # Apply EQ gains
        gains = {
            "sub_bass": 1.2,
            "bass": 1.1,
            "low_mids": 0.9,
            "high_mids": 1.1,
            "highs": 1.05
        }
        
        # Apply band-specific gains
        freqs = librosa.fft_frequencies(sr=sr)
        for band, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs <= high)
            D[mask] *= gains[band]
        
        # Convert back to time domain
        return librosa.istft(D)
    
    def _enhance_stereo(self, audio: np.ndarray) -> np.ndarray:
        """Enhance stereo field"""
        # Create pseudo-stereo effect
        left = audio.copy()
        right = audio.copy()
        
        # Apply slight delay and phase shift to right channel
        delay_samples = int(0.02 * 44100)  # 20ms delay
        right = np.roll(right, delay_samples)
        
        # Combine channels
        stereo = np.vstack((left, right))
        
        return stereo
    
    def _apply_limiting(self, audio: np.ndarray) -> np.ndarray:
        """Apply limiting and normalization"""
        # Find peak value
        peak = np.max(np.abs(audio))
        
        # Calculate target gain
        target_peak = 10 ** (self.target_peak / 20)
        gain = min(target_peak / peak, 1.0)
        
        # Apply gain
        processed = audio * gain
        
        # Apply limiting
        mask = np.abs(processed) > target_peak
        processed[mask] = np.sign(processed[mask]) * target_peak
        
        return processed
    
    def _calculate_audio_metrics(
        self, audio: np.ndarray, sr: int
    ) -> Dict[str, float]:
        """Calculate audio metrics for metadata"""
        return {
            "peak_db": float(20 * np.log10(np.max(np.abs(audio)))),
            "rms_db": float(20 * np.log10(np.sqrt(np.mean(audio**2)))),
            "duration": float(len(audio) / sr),
            "sample_rate": sr
        }

# Initialize global master
_master = None

async def master_audio(audio_path: str) -> str:
    """Main function to master audio"""
    global _master
    if _master is None:
        _master = AudioMaster()
    return await _master.master_audio(audio_path)
