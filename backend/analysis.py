import json
import os
import io
import subprocess
import numpy as np
import librosa
import whisper
import soundfile as sf
import google.generativeai as genai

def decode_webm_to_wav(webm_bytes: bytes) -> np.ndarray:
    """
    Decodes a WEBM byte stream to a WAV-like NumPy array using FFmpeg.
    """
    command = [
        'ffmpeg',
        '-i', 'pipe:0',          # Input from stdin
        '-f', 'wav',             # Output format WAV
        '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian codec
        '-ar', '16000',          # Audio sample rate 16kHz
        '-ac', '1',              # Mono channel
        'pipe:1'                 # Output to stdout
    ]
    
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_data, stderr_data = process.communicate(input=webm_bytes)
    
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {stderr_data.decode()}")

    # Load the WAV data from stdout into a NumPy array
    wav_io = io.BytesIO(stdout_data)
    audio_array, samplerate = sf.read(wav_io)
    
    return audio_array

def transcribe_audio(file_path: str) -> str:
    """
    Transcribes an audio file using the Whisper base model.
    """
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]

def transcribe_audio_chunk(audio_chunk_bytes: bytes) -> str:
    """
    Transcribes a small audio chunk using the Whisper base model after decoding.
    """
    try:
        audio_array = decode_webm_to_wav(audio_chunk_bytes)
        # Convert to float32 as whisper expects
        audio_array = audio_array.astype(np.float32)
        model = whisper.load_model("base")
        result = model.transcribe(audio_array, fp16=False)
        return result["text"]
    except (RuntimeError, sf.SoundFileError) as e:
        print(f"Error during chunk transcription: {e}")
        return ""

def analyze_chunk_for_fillers(transcript: str) -> list:
    """
    Analyzes a small transcript chunk for common filler words.
    """
    filler_words = ["um", "uh", "like", "so", "you know"]
    found_fillers = []
    # Use word boundaries to avoid matching parts of words (e.g., "rum" in "drum")
    for word in filler_words:
        if f" {word} " in f" {transcript.lower()} ":
            found_fillers.append(word)
    return found_fillers

def analyze_pitch_chunk(audio_chunk_bytes: bytes) -> dict:
    """
    Performs a lightweight pitch analysis on an audio chunk after decoding.
    """
    try:
        audio_array = decode_webm_to_wav(audio_chunk_bytes)
        # Ensure the array is float32, as required by librosa
        y = audio_array.astype(np.float32)
        sr = 16000  # Sample rate is fixed by our decoding step
        
        f0, voiced_flag, _ = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
        )
        voiced_f0 = f0[voiced_flag]
        pitch_variance = np.std(voiced_f0) if voiced_f0.size > 0 else 0
        return {"pitch_variance_chunk": pitch_variance}
    except (RuntimeError, sf.SoundFileError) as e:
        print(f"Error during pitch chunk analysis: {e}")
        return {"pitch_variance_chunk": 0}

def analyze_vocal_delivery(file_path: str, transcript: str) -> dict:
    """
    Analyzes the vocal delivery of a speech from an audio file.
    """
    y, sr = librosa.load(file_path)
    word_count = len(transcript.split())
    duration = librosa.get_duration(y=y, sr=sr)
    speaking_rate = (word_count / duration) * 60 if duration > 0 else 0

    f0, voiced_flag, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
    )
    voiced_f0 = f0[voiced_flag]
    pitch_variance = np.std(voiced_f0) if voiced_f0.size > 0 else 0

    non_silent_intervals = librosa.effects.split(y, top_db=20)
    long_pauses_count = 0
    if len(non_silent_intervals) > 1:
        for i in range(len(non_silent_intervals) - 1):
            pause_duration = (non_silent_intervals[i+1][0] - non_silent_intervals[i][1]) / sr
            if pause_duration > 1.5:
                long_pauses_count += 1

    num_points = 100
    pitch_over_time = np.interp(np.linspace(0, len(voiced_f0), num_points), np.arange(len(voiced_f0)), voiced_f0).tolist() if voiced_f0.size > 0 else []

    pace_over_time = []
    chunk_size_seconds = 5
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
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    prompt = f"""
    Analyze the following speech transcript and provide the following metrics in a JSON format:
    1.  **filler_word_counts**: A dictionary of common filler words and their counts.
    2.  **clarity_score**: An integer score from 1 to 10 for speech clarity.
    3.  **suggestions**: A list of 3-5 actionable suggestions for improvement.
    4.  **improved_sentence**: An example sentence with suggestions applied.

    Transcript:
    "{transcript}"

    Return ONLY the JSON object.
    """

    try:
        response = model.generate_content(prompt)
        json_string = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(json_string)
    except Exception as e:
        print(f"An error occurred during API call: {e}")
        return {
            "filler_word_counts": {},
            "clarity_score": 0,
            "suggestions": ["Failed to analyze content due to an API error."],
            "improved_sentence": "N/A",
        }
