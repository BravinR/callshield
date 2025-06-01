from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates 
from typing import List, Dict
from whispercpp import Whisper
import os
import aiofiles
import subprocess
import asyncio
from pydub import AudioSegment
import io
import json

from backend.model import llama_request

app = FastAPI()
whisper_model = Whisper('small')
ffmpeg_processes: Dict[int, subprocess.Popen] = {}

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
    client_port = websocket.client.port
    print(f"Client connected: {websocket.client.host}:{client_port}")

    try:
        while True:
            # Add timeout to prevent indefinite blocking
            try:
                message = await asyncio.wait_for(websocket.receive(), timeout=30.0)
            except asyncio.TimeoutError:
                print(f"WebSocket timeout for client {client_port}")
                continue
            
            if "text" in message:
                data = message["text"]
                print(f"Received text: {data}")
                await manager.broadcast_text(f"Text from client: {data}")
                
            elif "bytes" in message:
                audio_data = message["bytes"]
                print(f"Received {len(audio_data)} bytes of audio data from {client_port}")
                
                try:
                    # Convert received bytes (WebM) to WAV
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
                    
                    # Convert to WAV format (16kHz, mono, 16-bit for Whisper optimization)
                    audio_segment = audio_segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)
                    
                    # Create audio uploads directory
                    os.makedirs("audio_uploads", exist_ok=True)
                    
                    # Save as WAV file
                    wav_filename = f"audio_uploads/received_audio_{client_port}_{asyncio.get_event_loop().time()}.wav"
                    audio_segment.export(wav_filename, format="wav")
                    
                    print(f"Converted audio saved as: {wav_filename}")
                    
                    # Transcribe the WAV file
                    try:
                        result = whisper_model.transcribe(wav_filename)
                        text = whisper_model.extract_text(result)
                        if text:
                            print(f"Transcribed for {client_port}: {text}")
                            await websocket.send_text(f"Transcription: {text}")

                            llama_output = llama_request.run_llama_request(text[0])
                            completion_text = json.loads(llama_output["completion_message"]["content"]["text"])
                            scam_score = completion_text["scam_score"]
                            explanation = completion_text["explanation"]

                            await websocket.send_text(f"Scam Score: {scam_score}")
                            await websocket.send_text(f"Explanation: {explanation}")
                        else:
                            print(f"No text transcribed for {client_port}")
                            
                    except Exception as e:
                        print(f"Error during transcription for {client_port}: {e}")
                    
                    # Optional: Save original WebM data as well
                    try:
                        webm_filename = f"audio_uploads/original_{client_port}_{asyncio.get_event_loop().time()}.webm"
                        async with aiofiles.open(webm_filename, "wb") as f:
                            await f.write(audio_data)
                    except Exception as e:
                        print(f"Error saving original audio for {client_port}: {e}")
                    
                    await manager.broadcast_text(f"Processed audio chunk of length: {len(audio_data)}")
                    
                except Exception as e:
                    print(f"Error converting audio for {client_port}: {e}")
                    await websocket.send_text(f"Error processing audio: {str(e)}")

    except WebSocketDisconnect:
        print(f"Client {client_port} disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error for {client_port}: {e}")
        manager.disconnect(websocket)
    finally:
        print(f"Cleaned up resources for client {client_port}")