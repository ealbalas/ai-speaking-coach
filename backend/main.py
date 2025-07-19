import logging
import os
import uuid
from io import BytesIO

from analysis import analyze_content, analyze_vocal_delivery, transcribe_audio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment

# --- Load Environment Variables ---
# This will load the .env file located in the same directory (backend/)
load_dotenv()

# --- Configuration ---
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows the Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("--- SERVER STARTUP ---")
    logger.info("Audio files will be saved to the '%s' directory.", AUDIO_DIR)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    logger.info(
        f"Client connected: {websocket.client.host}:{websocket.client.port} (Session: {session_id})"
    )

    # Send the session_id to the client immediately after connection
    await websocket.send_json({"session_id": session_id})

    audio_buffer = BytesIO()

    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer.write(data)
    except WebSocketDisconnect:
        logger.warning(
            f"Client disconnected. Processing audio for session {session_id}..."
        )

        if audio_buffer.tell() > 0:
            audio_buffer.seek(0)

            try:
                audio_segment = AudioSegment.from_file(audio_buffer, format="webm")
                output_path = os.path.join(AUDIO_DIR, f"{session_id}.wav")
                audio_segment.export(output_path, format="wav")
                logger.info(
                    f"Successfully saved audio for session {session_id} at {output_path}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to process audio for session {session_id}. Error: {e}"
                )
        else:
            logger.info(
                f"No audio data received for session {session_id}. Nothing to save."
            )


@app.get("/analysis/{session_id}")
async def get_analysis(session_id: str):
    """
    Analyzes the audio file for a given session and returns a full report.
    """
    logger.info(f"Starting analysis for session {session_id}...")
    file_path = os.path.join(AUDIO_DIR, f"{session_id}.wav")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found.")

    try:
        # 1. Transcribe Audio
        transcript = transcribe_audio(file_path)

        # 2. Analyze Vocal Delivery
        vocal_delivery_metrics = analyze_vocal_delivery(file_path)

        # 3. Analyze Content
        content_metrics = analyze_content(transcript)

        # 4. Combine Results
        full_report = {
            "transcript": transcript,
            "vocal_delivery": vocal_delivery_metrics,
            "content": content_metrics,
        }

        logger.info(f"Successfully generated analysis for session {session_id}.")
        return full_report

    except Exception as e:
        logger.error(f"An error occurred during analysis for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze audio.")


@app.get("/")
async def get():
    return {"message": "AI Speaking Coach backend is running. Connect via WebSocket."}
