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
