import whisper
import librosa

model = whisper.load_model("base")

def transcribe_audio(file_path: str) -> str:
    # Load audio using librosa at 16000 Hz, which is the sample rate expected by Whisper.
    # This bypasses Whisper's internal call to the FFmpeg command-line tool,
    # preventing WinError 2 (FileNotFoundError) when FFmpeg is not installed.
    audio, sr = librosa.load(file_path, sr=16000)
    result = model.transcribe(audio, language="en")
    return result["text"].strip()