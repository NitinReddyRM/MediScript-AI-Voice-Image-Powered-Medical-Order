import librosa
import noisereduce as nr
from pydub import AudioSegment, effects
import numpy as np
import soundfile as sf
import io
class preprocess:

    @staticmethod
    def preprocess_audio(uploaded_file, target_sr=16000):
        """
        Preprocess audio for ASR:
        1. Load and resample
        2. Normalize volume
        3. Denoise
        4. Trim silence
        5. Export as cleaned WAV
        """
        
        # --- Step 1: Convert file (mp3/m4a/wav) to wav using pydub ---
        audio = AudioSegment.from_file(uploaded_file)
        audio = audio.set_channels(1)   # mono
        audio = audio.set_frame_rate(target_sr)  # resample
        
        # Normalize loudness
        audio = effects.normalize(audio)
        
        # Export to raw wav in memory
        buf = io.BytesIO()
        audio.export(buf, format="wav")
        buf.seek(0)
        
        # --- Step 2: Load with librosa ---
        y, sr = librosa.load(buf, sr=target_sr)
        
        # --- Step 3: Noise reduction ---
        reduced_noise = nr.reduce_noise(y=y, sr=sr)
        
        # --- Step 4: Trim silence ---
        y_trimmed, _ = librosa.effects.trim(reduced_noise, top_db=20)
        
        # --- Step 5: Save cleaned wav to memory ---
        cleaned_audio_buf = io.BytesIO()
        sf.write(cleaned_audio_buf, y_trimmed, sr, format="WAV")
        cleaned_audio_buf.seek(0)
        
        return cleaned_audio_buf
