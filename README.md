# CallShield
CallShield is a Python-based application powered by Llama 4 designed to detect scam calls in any language.
It was built for the 2025 Llama 4 Hackathon in NYC hosted by Cerebral Valley and Meta.

It leverages the Whisper AI model for speech-to-text transcription and Llama 4 for real-time call transcript analysis and scam detection.

## Technologies
- **Llama 4 Api**: For natural language processing and scam detection
- **Whisper.cpp**: For speech-to-text transcription
- **FastAPI**: For building the web application
- **Python**: For the backend logic
- **HTML/CSS/JavaScript**: For the frontend interface
- **Websockets**: For real-time communication between the client and server
- **FFmpeg**: For audio processing

## Getting Started
### Prerequisites
- Python 3.8 or higher
- Mac or Unix-based operating system (Or Windows with WSL)
- FFmpeg installed
- Llama 4 API key

### Installation, Configuration, and Running the Application
1. Clone the repository:
   ```bash
   git clone https://github.com/BravinR/callshield.git
   cd callshield
    ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the required packages:
   ```bash
    pip install -r backend/requirements.txt
    ```
4. Set up the environment variables:
   ```bash
   export LLAMA_KEY="<your_llama_api_key>"
   ```
5. Set the python path to the virtual environment:
   ```bash
   export PYTHONPATH=$(pwd)
   ```
6. Start the FastAPI server:
   ```bash
   cd backend
   fastapi dev main
    ```
7. Open your web browser and navigate to `http://localhost:8000` to access the application. Simply press the call button and speak into the microphone to start scam detection!

### How it Works
1. **Audio Capture**: The application captures audio from the user's microphone in real-time
2. **Speech-to-Text Transcription**: 7-second captured audio chunks are sent to the backend
3. **File Conversion**: The audio is converted from .webm to .wav using FFmpeg, a format compatible with Whisper.cpp
4. **Language Detection**: The language of the audio is detected using Whisper.cpp
5. **Transcription**: The audio is transcribed to text in any language using Whisper.cpp
6. **Scam Detection**: The transcribed text is sent to the Llama 4 API for scam detection
   1. Every 7 seconds, the application sends the transcribed text to the Llama 4 API
   2. The text is appended to the previous text for context so the entire up-to-date conversation is sent
7. **Scam Score Calculation**: The Llama 4 model calculated a scam score for any input language
8. **Real-time Updates**: If a high scam score is outputted, the application uses Websockets to send a real-time notification to the user to display a warning message

## Other sources:
[hyqshr/whispercpp-fastapi](https://github.com/hyqshr/whispercpp-fastapi)
