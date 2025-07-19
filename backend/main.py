from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    This endpoint handles WebSocket connections.
    It accepts a connection, listens for text messages,
    and sends a response back.
    """
    await websocket.accept()
    print(f"Client connected: {websocket.client.host}")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message: {data}")
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print(f"Client disconnected: {websocket.client.host}")
