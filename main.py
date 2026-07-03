import os
import torch
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq
from omnivoice import OmniVoice

app = FastAPI()

# Enable cross-origin calls so your frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq and Voice (Make sure 'me.wav' exists in your repo root)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", load_asr=True)
REFERENCE_AUDIO = "me.wav"

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # Build systemic chat flow structure
        messages = [{"role": "system", "content": "You are Papa Jerry. Keep responses concise — 2 to 4 sentences."}]
        messages.extend(req.history)
        messages.append({"role": "user", "content": req.message})
        
        # Pull text completion array from Groq
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=300
        )
        bot_text = completion.choices[0].message.content
        
        # Zero-shot voice cloning pipeline synthesis execution
        audio = model.generate(text=bot_text, ref_audio=REFERENCE_AUDIO)
        
        # Write 24kHz audio track to temporary file output
        output_path = "output.wav"
        sf.write(output_path, audio[0], 24000)
        
        return {"text": bot_text, "audio_url": "/audio"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio")
async def get_audio():
    if os.path.exists("output.wav"):
        return FileResponse("output.wav", media_type="audio/wav")
    raise HTTPException(status_code=404, detail="Audio file generation missing or incomplete")
