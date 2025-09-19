from dotenv import load_dotenv
import os
from .LLM_model import LLM_MODEL
import tempfile
import io
from pydub import AudioSegment
from .Audio_preprocessing import preprocess
from faster_whisper import WhisperModel

llm_model=LLM_MODEL()
load_dotenv()
class orchetraction:
    def __init__(self):
        # Load the model (options: tiny, base, small, medium, large)
        self.Whisper_model = WhisperModel("base", compute_type="int8")  # "int8" = fast, low-resource


    def speech_to_text(self,audio_file):
        """
        Convert uploaded audio (MP3, WAV, M4A) to text.
        `audio_file` should be a file-like object (e.g., from Streamlit upload).
        """
        # Determine file type
        print(audio_file.name)
        file_ext = audio_file.name.split('.')[-1].lower()
        if file_ext in ["mp3", "m4a"]:
            # Save uploaded file to a temp file first
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"{file_ext}") as tmp_in:
                tmp_in.write(audio_file.read())
                tmp_in_path = tmp_in.name
            print(tmp_in_path)
            # Load from temp file and convert to wav
            audio_segment = AudioSegment.from_file(tmp_in_path, format=file_ext)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
                audio_segment.export(tmp_out.name, format="wav")
                tmp_path = tmp_out.name
        elif file_ext == "wav":
            # Save uploaded WAV directly
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name
        else:
            raise ValueError("Unsupported audio format. Please upload MP3, WAV, or M4A.")
        # Load and run the model
        segments, info = self.Whisper_model.transcribe(preprocess.preprocess_audio(tmp_path))
        
        
        return llm_model.parse_input(" ".join([i.text for i in segments]))




        

