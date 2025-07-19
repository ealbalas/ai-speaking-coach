import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <p>Open your browser's developer console to see connection messages.</p>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            console.log("Attempting to connect to WebSocket...");
            var ws = new WebSocket("ws://localhost:8000/ws");

            ws.onopen = function(event) {
                console.log("WebSocket connection established.");
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode("[Connected]");
                message.appendChild(content);
                messages.appendChild(message);
            };

            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };

            ws.onclose = function(event) {
                console.log("WebSocket connection closed.");
            };

            ws.onerror = function(event) {
                console.error("WebSocket error observed:", event);
            };

            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.on_event("startup")
async def startup_event():
    logger.info("--- SERVER STARTUP ---")

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"Client connected: {websocket.client.host}:{websocket.client.port}")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}")
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        logger.warning("Client disconnected")
