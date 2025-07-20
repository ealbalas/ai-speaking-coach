import json
import os

import google.generativeai as genai
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


def analyze_vocal_delivery(file_path: str, transcript: str) -> dict:
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
    word_count = len(transcript.split())
    duration = librosa.get_duration(y=y, sr=sr)
    speaking_rate = (word_count / duration) * 60 if duration > 0 else 0

    # 2. Calculate Pitch Variance (Monotone Score)
    f0, voiced_flag, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
    )
    voiced_f0 = f0[voiced_flag]

    # Filter out unvoiced frames (NaNs) before calculating variance
    # voiced_f0 = f0[~np.isnan(f0)]
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

    # --- 2. TIME-SERIES DATA (for charts) ---

    # Pitch Over Time
    # Downsample to 100 points for a clean chart visualization
    num_points = 100
    if len(voiced_f0) > num_points:
        indices = np.linspace(0, len(voiced_f0) - 1, num=num_points, dtype=int)
        pitch_over_time = voiced_f0[indices].tolist()
    else:
        pitch_over_time = voiced_f0.tolist()

    # Pace Over Time (WPM in chunks)
    pace_over_time = []
    chunk_size_seconds = 5  # Calculate WPM every 5 seconds
    num_chunks = int(duration / chunk_size_seconds)

    if num_chunks > 1:
        words_per_chunk = word_count / num_chunks
        for _ in range(num_chunks):
            wpm_chunk = (words_per_chunk / chunk_size_seconds) * 60
            pace_over_time.append(wpm_chunk)

    return {
        "speaking_rate": speaking_rate,
        "pitch_variance": pitch_variance,
        "long_pauses_count": long_pauses_count,
        "pitch_over_time": pitch_over_time,
        "pace_over_time": pace_over_time,
    }


def analyze_content(transcript: str) -> dict:
    """
    Analyzes the content of a speech transcript using a Large Language Model.

    Args:
        transcript: The speech transcript.

    Returns:
        A dictionary containing the following metrics:
        - filler_word_counts: A dictionary of filler words and their counts.
        - clarity_score: A score from 1 to 10 on the clarity of the speech.
        - suggestions: A list of suggestions for improvement.
    """
    # For security, it's recommended to set the API key as an environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    prompt = f"""
    Analyze the following speech transcript and provide the following metrics in a JSON format:
    1.  **filler_word_counts**: A dictionary where keys are common filler words (e.g., "um", "uh", "like", "so", "you know") and values are their counts in the transcript.
    2.  **clarity_score**: An integer score from 1 (very unclear) to 10 (very clear) representing the overall clarity of the speech.
    3.  **suggestions**: A list of 3-5 specific and actionable suggestions for improving the content and clarity of the speech.
    4.  **improved_sentence: An example of the sentence with suggestions.

    Transcript:
    "{transcript}"

    Please return ONLY the JSON object.
    """

    try:
        response = model.generate_content(prompt)
        # The response text might be enclosed in ```json ... ```, so we need to extract it.
        json_string = (
            response.text.strip().replace("```json", "").replace("```", "").strip()
        )
        return json.loads(json_string)
    except Exception as e:
        print(f"An error occurred during API call: {e}")
        return {
            "filler_word_counts": {},
            "clarity_score": 0,
            "suggestions": ["Failed to analyze content due to an API error."],
            "improved_sentence": ["Failed to analyze content due to an API error."],
        }
