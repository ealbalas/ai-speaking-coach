import logging
import os
import uuid
from io import BytesIO
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydub import AudioSegment

# --- Configuration ---
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("--- SERVER STARTUP ---")
    logger.info("Audio files will be saved to the '%s' directory.", AUDIO_DIR)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    logger.info(f"Client connected: {websocket.client.host}:{websocket.client.port} (Session: {session_id})")
    
    # Accumulate all received audio chunks in a single byte buffer
    audio_buffer = BytesIO()

    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer.write(data)
    except WebSocketDisconnect:
        logger.warning(f"Client disconnected. Processing audio for session {session_id}...")
        
        # Ensure we have received some data before trying to process it
        if audio_buffer.tell() > 0:
            audio_buffer.seek(0)  # Rewind the buffer to the beginning
            
            try:
                # Use pydub to read the in-memory WebM/Opus audio
                # and export it as a WAV file.
                audio_segment = AudioSegment.from_file(audio_buffer, format="webm")
                
                # Define the output file path
                output_path = os.path.join(AUDIO_DIR, f"{session_id}.wav")
                
                # Export the audio to WAV format
                audio_segment.export(output_path, format="wav")
                
                logger.info(f"Successfully saved audio for session {session_id} at {output_path}")
            except Exception as e:
                logger.error(f"Failed to process audio for session {session_id}. Error: {e}")
        else:
            logger.info(f"No audio data received for session {session_id}. Nothing to save.")

@app.get("/")
async def get():
    return {"message": "AI Speaking Coach backend is running. Connect via WebSocket."}
