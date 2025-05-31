from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates 
from typing import List
import asyncio
import os
import aiofiles

app = FastAPI()


templates = Jinja2Templates(directory="templates")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected: {websocket.client}")

    async def broadcast_text(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def broadcast_bytes(self, message: bytes):
        for connection in self.active_connections:
            await connection.send_bytes(message)

manager = ConnectionManager()

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.websocket("/ws/audio")
async def websocket_endpoint_audio(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive()
            
            if "text" in message:
                data = message["text"]
                print(f"Received text: {data}")
                await manager.broadcast_text(f"Text from client: {data}")
            elif "bytes" in message:
                audio_data = message["bytes"]
                print(f"Received {len(audio_data)} bytes of audio data.")
                try:
                    os.makedirs("audio_uploads", exist_ok=True)
                    async with aiofiles.open(f"audio_uploads/received_audio_{websocket.client.port}.webm", "ab") as f:
                        await f.write(audio_data)
                except Exception as e:
                    print(f"Error saving audio chunk: {e}")
                await manager.broadcast_text(f"We received the whole video of length: {len(audio_data)}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(websocket)