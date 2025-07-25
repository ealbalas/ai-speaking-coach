import logging
import os
import uuid
import asyncio
from io import BytesIO

from analysis import (
    analyze_content,
    analyze_vocal_delivery,
    transcribe_audio,
    transcribe_audio_chunk,
    analyze_chunk_for_fillers,
    analyze_pitch_chunk,
    decode_webm_to_wav 
)
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import soundfile as sf

# --- Load Environment Variables ---
load_dotenv()

# --- Configuration ---
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)
CHUNK_DURATION_SECONDS = 3  # Analyze every 3 seconds
WEBSOCKET_BUFFER_SECONDS = 1 # Buffer 1 second of audio before processing a chunk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- CORS Middleware ---
# This is crucial for allowing the Vercel frontend to communicate with this backend.
# We read the frontend URL from an environment variable for flexibility.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

origins = [
    FRONTEND_URL,
    # You can add more static origins here if needed
]

# Allow all Vercel preview deployments
if "vercel.app" in FRONTEND_URL:
    origins.append("*.vercel.app")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        del self.active_connections[session_id]

    async def send_json(self, session_id: str, data: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(data)

manager = ConnectionManager()

async def audio_processing_task(session_id: str, websocket: WebSocket):
    full_audio_bytes = bytearray()
    chunk_buffer = bytearray()
    header = None
    
    try:
        while True:
            data = await websocket.receive_bytes()
            if header is None:
                header = data
            
            full_audio_bytes.extend(data)
            chunk_buffer.extend(data)

            # Simple duration estimation (highly approximate)
            # A 48kHz/16-bit mono stream is ~96kB/s. A webm/opus is much smaller.
            # This threshold is a heuristic to trigger analysis, not a precise measure.
            if len(chunk_buffer) > 15000 * CHUNK_DURATION_SECONDS: # ~15-20kBps for opus
                logger.info(f"Processing chunk for session {session_id}, buffer size: {len(chunk_buffer)} bytes")
                
                # Perform Chunk Analysis in a non-blocking way
                # We prepend the header to the current chunk to make it a valid WebM stream
                analysis_bytes = header + bytes(chunk_buffer)
                asyncio.create_task(analyze_and_feedback(session_id, analysis_bytes))

                # Reset chunk buffer
                chunk_buffer.clear()

    except WebSocketDisconnect:
        logger.warning(f"Client disconnected. Saving full audio for session {session_id}...")
        if full_audio_bytes:
            save_final_audio(session_id, bytes(full_audio_bytes))
        else:
            logger.info(f"No audio data received for session {session_id}.")
    finally:
        manager.disconnect(session_id)

async def analyze_and_feedback(session_id: str, audio_bytes: bytes):
    try:
        transcript_chunk = transcribe_audio_chunk(audio_bytes)
        if transcript_chunk:
            logger.info(f"Chunk transcript for {session_id}: {transcript_chunk}")
            filler_words = analyze_chunk_for_fillers(transcript_chunk)
            if filler_words:
                logger.info(f"Filler words detected for {session_id}: {filler_words}")
                await manager.send_json(session_id, {
                    "type": "FILLER_WORD",
                    "words": filler_words
                })
    except Exception as e:
        logger.error(f"Error during chunk analysis for session {session_id}: {e}")

def save_final_audio(session_id: str, audio_bytes: bytes):
    try:
        # Decode the entire stream to WAV for final storage
        audio_array = decode_webm_to_wav(audio_bytes)
        output_path = os.path.join(AUDIO_DIR, f"{session_id}.wav")
        
        # Save as WAV file
        sf.write(output_path, audio_array, 16000) # 16kHz as per our decode spec
        logger.info(f"Successfully saved audio for session {session_id} at {output_path}")

    except Exception as e:
        logger.error(f"Failed to process and save final audio for session {session_id}. Error: {e}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    session_id = str(uuid.uuid4())
    await manager.connect(websocket, session_id)
    logger.info(f"Client connected: {websocket.client.host}:{websocket.client.port} (Session: {session_id})")
    
    await manager.send_json(session_id, {"session_id": session_id})
    
    await audio_processing_task(session_id, websocket)


@app.get("/analysis/{session_id}")
async def get_analysis(session_id: str):
    logger.info(f"Starting analysis for session {session_id}...")
    file_path = os.path.join(AUDIO_DIR, f"{session_id}.wav")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found.")

    try:
        transcript = transcribe_audio(file_path)
        vocal_delivery_metrics = analyze_vocal_delivery(file_path, transcript)
        content_metrics = analyze_content(transcript)

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
async def root():
    return {"message": "AI Speaking Coach backend is running. Connect via WebSocket."}

if __name__ == "__main__":
    import uvicorn
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
