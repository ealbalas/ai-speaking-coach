import os
from unittest.mock import MagicMock

import numpy as np
import pytest
from analysis import analyze_vocal_delivery, transcribe_audio


@pytest.fixture(autouse=True)
def create_dummy_audio_file():
    """Creates a dummy audio directory and file for tests to use."""
    audio_dir = "audio_files"
    dummy_file_path = os.path.join(audio_dir, "dummy_audio.wav")

    # Create directory if it doesn't exist
    os.makedirs(audio_dir, exist_ok=True)

    # Create an empty dummy file
    with open(dummy_file_path, "w") as f:
        pass

    yield  # This allows the test to run

    # Teardown: Clean up the dummy file and directory after the test
    os.remove(dummy_file_path)
    if not os.listdir(audio_dir):
        os.rmdir(audio_dir)


@pytest.fixture
def mock_dependencies(mocker):
    """Mocks all external dependencies for analysis functions."""
    mocker.patch(
        "analysis.transcribe_audio", return_value="This is a five-word transcription"
    )
    mocker.patch(
        "analysis.librosa.load", return_value=(np.random.randn(22050 * 5), 22050)
    )
    mocker.patch("analysis.librosa.get_duration", return_value=5.0)
    mocker.patch(
        "analysis.librosa.pyin",
        return_value=(np.array([100.0, 110.0, 105.0, np.nan]), None, None),
    )
    mocker.patch(
        "analysis.librosa.effects.split",
        return_value=np.array([[0, 1 * 22050], [3 * 22050, 5 * 22050]]),
    )


def test_transcribe_audio(mocker):
    """
    Tests the transcribe_audio function to ensure it returns the correct transcription text.
    """
    # Mock the whisper library
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "This is a test transcription."}

    mock_whisper = mocker.patch("analysis.whisper.load_model", return_value=mock_model)

    # Call the function with a dummy file path
    file_path = "audio_files/dummy_audio.wav"
    transcription = transcribe_audio(file_path)

    # Assert the result
    assert transcription == "This is a test transcription."

    # Verify that the whisper functions were called correctly
    mock_whisper.assert_called_once_with("base")
    mock_model.transcribe.assert_called_once_with(file_path)


def test_analyze_vocal_delivery(mock_dependencies):
    """
    Tests the analyze_vocal_delivery function with mocked dependencies.
    """
    file_path = "audio_files/dummy_audio.wav"
    metrics = analyze_vocal_delivery(file_path)

    # 1. Test Speaking Rate
    # "This is a five-word transcription." = 5 words
    # Mocked duration is 5.0 seconds
    # Expected WPM = (5 words / 5 seconds) * 60 = 60
    assert "speaking_rate" in metrics
    assert metrics["speaking_rate"] == 60.0

    # 2. Test Pitch Variance
    # Mocked f0 is [100.0, 110.0, 105.0, np.nan]
    # Voiced f0 is [100.0, 110.0, 105.0]
    # Expected variance is the standard deviation of the voiced f0
    expected_pitch_variance = np.std([100.0, 110.0, 105.0])
    assert "pitch_variance" in metrics
    assert np.isclose(metrics["pitch_variance"], expected_pitch_variance)

    # 3. Test Long Pauses
    # Mocked non-silent intervals: [[0, 1s], [3s, 5s]]
    # Pause is from 1s to 3s, duration = 2s
    # 2s > 1.5s, so there is 1 long pause
    assert "long_pauses_count" in metrics
    assert metrics["long_pauses_count"] == 1
