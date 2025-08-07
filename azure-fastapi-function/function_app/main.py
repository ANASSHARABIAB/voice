import os
from fastapi import FastAPI, File, UploadFile, HTTPException
import requests
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Environment variables for Azure OpenAI
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

# Full URL of Whisper endpoint
FULL_URL = AZURE_OPENAI_ENDPOINT

app = FastAPI()

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="function_app/static"), name="static")

@app.get("/")
def read_index():
    """Serve the index HTML for the root path"""
    return FileResponse("function_app/static/index.html")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Endpoint to transcribe uploaded WAV audio files using Azure OpenAI Whisper"""
    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are supported.")

    headers = {"api-key": AZURE_OPENAI_API_KEY}
    files = {
        "file": (file.filename, await file.read(), "audio/wav"),
        "response_format": (None, "json"),
        "language": (None, "en"),
    }

    try:
        response = requests.post(FULL_URL, headers=headers, files=files)
        response.raise_for_status()
    except requests.HTTPError as e:
        # Return error details to client
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "details": response.text},
        )

    data = response.json()
    transcript = data.get("text", "")
    return {"transcript": transcript}

@app.post("/process")
async def process_audio(file: UploadFile = File(...)):
    """Alias endpoint for compatibility"""
    return await transcribe_audio(file)
