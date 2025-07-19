from unittest.mock import MagicMock

from analysis import transcribe_audio


def test_transcribe_audio(mocker):
    """
    Tests the transcribe_audio function to ensure it returns the correct transcription text.
    """
    # Mock the whisper library
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "This is a test transcription."}

    # The path should be 'your_module_name.function_name'
    mock_whisper = mocker.patch("analysis.whisper")
    mock_whisper.load_model.return_value = mock_model

    # Call the function with a dummy file path
    file_path = "audio_files/dummy_audio.wav"
    transcription = transcribe_audio(file_path)

    # Assert the result
    assert transcription == "This is a test transcription."

    # Verify that the whisper functions were called correctly
    mock_whisper.load_model.assert_called_once_with("base")
    mock_model.transcribe.assert_called_once_with(file_path)
