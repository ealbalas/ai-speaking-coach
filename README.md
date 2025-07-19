# AI Speaking Coach

This project is a web application designed to help users improve their public speaking skills. It records a user's speech and saves it for future analysis.

## Features

- **Next.js Frontend**: A modern React-based frontend for a smooth user experience.
- **FastAPI Backend**: A high-performance Python backend for handling real-time data.
- **Real-time Audio Streaming**: Captures audio from the user's microphone and streams it to the server via WebSockets.
- **Audio Processing & Storage**: The backend processes the incoming audio stream and saves it as a `.wav` file upon session completion.
- **Connection Logging**: The backend logs client connections, disconnections, and audio processing status.
- **Audio Transcription**: Transcribes the user's speech to text using OpenAI's Whisper model.

## Audio Analysis

The `backend/analysis.py` module provides functions for analyzing the user's speech.

### `transcribe_audio(file_path)`

This function takes the path to an audio file as input and returns the transcription of the audio. It uses the `base` model of OpenAI's Whisper for efficiency.

### `analyze_vocal_delivery(file_path)`

This function analyzes the vocal delivery of a speech from an audio file and returns a dictionary of metrics, including:
- **Speaking Rate**: Words per minute.
- **Pitch Variance**: A score indicating how monotone the speech is.
- **Long Pauses**: The number of pauses longer than 1.5 seconds.

### `analyze_content(transcript)`

This function uses a Large Language Model (Google's Gemini) to analyze the content of the speech. It returns a dictionary with:
- **Filler Word Counts**: A count of common filler words.
- **Clarity Score**: A score from 1 to 10 on the clarity of the speech.
- **Suggestions**: Actionable suggestions for improvement.

## Getting Started

### System-Level Dependencies

This project requires **FFmpeg** for audio processing on the backend. Please install it on your system before running the application.

-   **On macOS (using Homebrew):**
    ```bash
    brew install ffmpeg
    ```
-   **On Debian/Ubuntu:**
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```
-   **On Windows:**
    Download the binaries from the [official FFmpeg website](https://ffmpeg.org/download.html) and add the `bin` directory to your system's PATH.

### Prerequisites

- Node.js and npm
- Python 3.7+ and pip

### API Key Setup

The content analysis feature uses the Google Gemini API. To use it, you need to get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and set it as an environment variable.

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

### Installation and Running

**Backend (FastAPI)**

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install the Python dependencies (including `pydub`):
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the development server:
    ```bash
    uvicorn main:app --reload
    ```
    The backend will be running at `http://localhost:8000`.

**Frontend (Next.js)**

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install the dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    The frontend will be running at `http://localhost:3000`.
