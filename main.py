import os
import scipy.io.wavfile
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pocket_tts import TTSModel

app = FastAPI()

# Enable Global Cross-Origin Resource Sharing (CORS) so your GitHub Page can talk to it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global memory variables for caching the model and your voice state
tts_model = None
voice_state = None
REFERENCE_VOICE = "my-voice.wav"
OUTPUT_FILE = "output.wav"

@app.on_event("startup")
def initialize_cloned_voice():
    global tts_model, voice_state
    try:
        print("Loading lightweight 100M-parameter TTS Model...")
        tts_model = TTSModel.load_model()
        
        if not os.path.exists(REFERENCE_VOICE):
            print(f"CRITICAL ERROR: {REFERENCE_VOICE} is missing from the directory!")
            return
            
        print("Extracting acoustic properties from your reference sample...")
        # Extracts voice signature once on startup to optimize speed
        voice_state = tts_model.get_state_for_audio_prompt(REFERENCE_VOICE)
        print("Voice successfully cloned. Server is online!")
    except Exception as e:
        print(f"Initialization failure: {str(e)}")

class TextRequest(BaseModel):
    text: str

@app.post("/clone")
def generate_voice(request: TextRequest):
    if tts_model is None or voice_state is None:
        raise HTTPException(status_code=500, detail="The AI engine failed to load or reference voice is missing.")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
        
    try:
        # Run text inference through your cached cloned voice profile
        audio_tensor = tts_model.generate_audio(voice_state, request.text)
        
        # Save generated tensor directly to a standard wav audio file
        scipy.io.wavfile.write(OUTPUT_FILE, tts_model.sample_rate, audio_tensor.numpy())
        
        return FileResponse(OUTPUT_FILE, media_type="audio/wav", filename="cloned_voice.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health():
    return {"status": "operational"}
