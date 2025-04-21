
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
import uvicorn
import os
import torch
from pydub import AudioSegment
from TTS.api import TTS
from torch.serialization import safe_globals
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
from fastapi.middleware.cors import CORSMiddleware

# Setup
os.environ["COQUI_TOS_AGREED"] = "1"
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
with safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig]):
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", gpu=torch.cuda.is_available())
    # tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=torch.cuda.is_available())

os.makedirs("voices", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# 🔴 Record Voice API
@app.post("/record_voice")
async def record_voice(audio: UploadFile, user_id: str = Form(...)):
    voice_path = f"./voices/{user_id}.wav"
    audio_bytes = await audio.read()
    temp_path = f"./voices/temp_input.wav"
    with open(temp_path, "wb") as f:
        f.write(audio_bytes)
    AudioSegment.from_file(temp_path).export(voice_path, format="wav")
    os.remove(temp_path)
    return {"message": f"Voice saved for ID: {user_id}"}

 

@app.post("/speak_caption")
async def generate_voice(user_id: str = Form(...), text: str = Form(...)):
    voice_path = f"./voices/{user_id}.wav"
    if not os.path.exists(voice_path):
        return {"error": "Voice sample not found."}

    output_path = f"./outputs/{user_id}_{abs(hash(text)) % 100000}_out.wav"
    tts.tts_to_file(
        text=text,
        speaker_wav=voice_path,
        language="en",
        file_path=output_path
    )

    return FileResponse(output_path, media_type="audio/wav", filename=os.path.basename(output_path), headers={
        "Content-Disposition": "inline"
    })

# Run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
