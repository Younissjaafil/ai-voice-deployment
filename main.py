
# from fastapi import FastAPI, UploadFile, Form
# from fastapi.responses import FileResponse
# import uvicorn
# import os
# import torch
# from pydub import AudioSegment
# from TTS.api import TTS
# from torch.serialization import safe_globals
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
# from TTS.config.shared_configs import BaseDatasetConfig
# from fastapi.middleware.cors import CORSMiddleware

# # Setup
# os.environ["COQUI_TOS_AGREED"] = "1"
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# with safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig]):
#     tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=torch.cuda.is_available())

# os.makedirs("voices", exist_ok=True)
# os.makedirs("outputs", exist_ok=True)

# # 🔴 Record Voice API
# @app.post("/record_voice")
# async def record_voice(audio: UploadFile, user_id: str = Form(...)):
#     voice_path = f"./voices/{user_id}.wav"
#     audio_bytes = await audio.read()
#     temp_path = f"./voices/temp_input.wav"
#     with open(temp_path, "wb") as f:
#         f.write(audio_bytes)
#     AudioSegment.from_file(temp_path).export(voice_path, format="wav")
#     os.remove(temp_path)
#     return {"message": f"Voice saved for ID: {user_id}"}

 

# @app.post("/speak_caption")
# async def generate_voice(user_id: str = Form(...), text: str = Form(...)):
#     voice_path = f"./voices/{user_id}.wav"
#     if not os.path.exists(voice_path):
#         return {"error": "Voice sample not found."}

#     output_path = f"./outputs/{user_id}_{abs(hash(text)) % 100000}_out.wav"
#     tts.tts_to_file(
#         text=text,
#         speaker_wav=voice_path,
#         language="en",
#         file_path=output_path
#     )

#     return FileResponse(output_path, media_type="audio/wav", filename=os.path.basename(output_path), headers={
#         "Content-Disposition": "inline"
#     })

# # Run the app
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000)

from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import os
import torch
from pydub import AudioSegment
from TTS.api import TTS
# Removed unused imports from original safe_globals context if not needed elsewhere
# from torch.serialization import safe_globals
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
# from TTS.config.shared_configs import BaseDatasetConfig
from fastapi.middleware.cors import CORSMiddleware
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup
os.environ["COQUI_TOS_AGREED"] = "1"
app = FastAPI()

# Allow all origins for simplicity in deployment.
# IMPORTANT: For production, restrict this to your frontend's domain(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Changed from ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- TTS Model Loading ---
# This might take time on first startup (cold start in serverless)
# The Dockerfile includes a step to pre-download the model.
TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
logger.info(f"Loading TTS model: {TTS_MODEL}...")
try:
    # Removed safe_globals context as it's often not strictly necessary
    # unless loading very old/specific checkpoints. Test if removal works.
    # If you encounter issues loading the model, you might need to re-add
    # the safe_globals context manager around this initialization.
    tts = TTS(model_name=TTS_MODEL, gpu=torch.cuda.is_available())
    logger.info("TTS model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading TTS model: {e}")
    # Depending on your strategy, you might want the app to fail startup
    # or handle requests differently if the model fails to load.
    tts = None # Indicate model loading failure

# Create directories if they don't exist
os.makedirs("voices", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# --- API Endpoints ---

@app.get("/health", status_code=200)
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "API is running"}

@app.post("/record_voice")
async def record_voice(audio: UploadFile, user_id: str = Form(...)):
    """Records (saves) a voice sample for a user."""
    if not audio:
        raise HTTPException(status_code=400, detail="No audio file provided.")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required.")

    voice_path = f"./voices/{user_id}.wav"
    temp_path = f"./voices/temp_{user_id}_input.wav" # Use unique temp name

    try:
        # Save uploaded file temporarily
        audio_bytes = await audio.read()
        with open(temp_path, "wb") as f:
            f.write(audio_bytes)

        # Convert to WAV using pydub
        logger.info(f"Converting uploaded audio for user {user_id} to WAV.")
        sound = AudioSegment.from_file(temp_path)
        sound.export(voice_path, format="wav")
        logger.info(f"Voice saved for ID: {user_id} at {voice_path}")

    except Exception as e:
        logger.error(f"Error processing voice for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process uploaded voice.")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        await audio.close() # Close the upload file

    return JSONResponse(content={"message": f"Voice saved for ID: {user_id}"})

@app.post("/speak_caption")
async def generate_voice(user_id: str = Form(...), text: str = Form(...)):
    """Generates speech from text using a previously recorded voice."""
    if tts is None:
         raise HTTPException(status_code=503, detail="TTS model is not available.")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required.")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required.")

    voice_path = f"./voices/{user_id}.wav"
    if not os.path.exists(voice_path):
        logger.warning(f"Voice sample not found for user_id: {user_id}")
        raise HTTPException(status_code=404, detail=f"Voice sample not found for user ID: {user_id}. Please record voice first.")

    # Sanitize text slightly for filename (optional)
    safe_text_hash = abs(hash(text)) % 100000
    output_filename = f"{user_id}_{safe_text_hash}_out.wav"
    output_path = f"./outputs/{output_filename}"

    try:
        logger.info(f"Generating speech for user {user_id} with text: '{text[:30]}...'")
        tts.tts_to_file(
            text=text,
            speaker_wav=voice_path,
            language="en", # Assuming English, make dynamic if needed
            file_path=output_path
        )
        logger.info(f"Speech generated successfully: {output_path}")

    except Exception as e:
        logger.error(f"TTS generation failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate speech.")

    return FileResponse(
        output_path,
        media_type="audio/wav",
        filename=output_filename,
        # Use 'attachment' if you want download, 'inline' tries to play in browser
        headers={"Content-Disposition": f"inline; filename=\"{output_filename}\""}
    )

# Run the app (for local development)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Added reload=True for dev