import librosa
import numpy as np
import whisper


def transcribe_audio(file_path: str) -> str:
    """
    Transcribes an audio file using the Whisper base model.

    Args:
        file_path: The path to the audio file.

    Returns:
        The transcription of the audio file.
    """
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]


def analyze_vocal_delivery(file_path: str) -> dict:
    """
    Analyzes the vocal delivery of a speech from an audio file.

    Args:
        file_path: The path to the audio file.

    Returns:
        A dictionary containing the following metrics:
        - speaking_rate: Words per minute.
        - pitch_variance: Standard deviation of the pitch.
        - long_pauses_count: Number of pauses longer than 1.5 seconds.
    """
    # Load the audio file
    y, sr = librosa.load(file_path)

    # 1. Calculate Speaking Rate (WPM)
    transcription = transcribe_audio(file_path)
    word_count = len(transcription.split())
    duration = librosa.get_duration(y=y, sr=sr)
    speaking_rate = (word_count / duration) * 60 if duration > 0 else 0

    # 2. Calculate Pitch Variance (Monotone Score)
    f0, _, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
    )
    # Filter out unvoiced frames (NaNs) before calculating variance
    voiced_f0 = f0[~np.isnan(f0)]
    pitch_variance = np.std(voiced_f0) if voiced_f0.size > 0 else 0

    # 3. Detect and Count Long Pauses
    # Split audio into non-silent segments
    non_silent_intervals = librosa.effects.split(y, top_db=20)
    long_pauses_count = 0
    if len(non_silent_intervals) > 1:
        for i in range(len(non_silent_intervals) - 1):
            pause_start = non_silent_intervals[i][1]
            pause_end = non_silent_intervals[i + 1][0]
            pause_duration = (pause_end - pause_start) / sr
            if pause_duration > 1.5:
                long_pauses_count += 1

    return {
        "speaking_rate": speaking_rate,
        "pitch_variance": pitch_variance,
        "long_pauses_count": long_pauses_count,
    }
