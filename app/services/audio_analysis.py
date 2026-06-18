import librosa
import numpy as np
import re

FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "literally", "actually", "so"]

def analyze_audio(file_path: str) -> dict:
    """
    Extract speech features from audio file using librosa.
    Returns speaking rate, pitch, pauses, and filler word counts.
    """
    # Load audio
    y, sr = librosa.load(file_path, sr=None)
    duration_secs = librosa.get_duration(y=y, sr=sr)

    # --- Pitch (fundamental frequency) ---
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7")
    )
    voiced_f0 = f0[voiced_flag] if voiced_flag is not None else np.array([])
    avg_pitch = float(np.nanmean(voiced_f0)) if len(voiced_f0) > 0 else 0.0
    pitch_variance = float(np.nanstd(voiced_f0)) if len(voiced_f0) > 0 else 0.0

    # --- Pauses (silent segments) ---
    intervals = librosa.effects.split(y, top_db=30)
    pause_count = max(0, len(intervals) - 1)

    # --- Speaking rate (estimated from voiced frames) ---
    voiced_duration = sum((e - s) / sr for s, e in intervals)
    speaking_rate_wpm = 0.0
    if voiced_duration > 0:
        # Approximate: average English speaker ~130 wpm
        # We estimate from voiced ratio vs typical syllable rate
        syllables_per_sec = 3.5
        estimated_words = voiced_duration * syllables_per_sec / 1.5
        speaking_rate_wpm = round((estimated_words / duration_secs) * 60, 1)

    return {
        "duration_secs": round(duration_secs, 1),
        "avg_pitch_hz": round(avg_pitch, 2),
        "pitch_variance": round(pitch_variance, 2),
        "pause_count": pause_count,
        "speaking_rate_wpm": speaking_rate_wpm,
    }

def count_filler_words(transcript: str) -> dict:
    """
    Count filler words in a transcript.
    Call this separately after transcription.
    """
    transcript_lower = transcript.lower()
    counts = {}
    total = 0
    for word in FILLER_WORDS:
        pattern = r'\b' + re.escape(word) + r'\b'
        count = len(re.findall(pattern, transcript_lower))
        if count > 0:
            counts[word] = count
            total += count
    return {"total": total, "breakdown": counts}