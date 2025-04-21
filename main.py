
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
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import torch
from pydub import AudioSegment
from TTS.api import TTS
import logging
import traceback
import time # For unique temp files

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
VOICES_DIR = "voices"
OUTPUTS_DIR = "outputs"
# For Runpod testing, allow all origins. Refine for production.
ALLOWED_ORIGINS = ["*"]
# ALLOWED_ORIGINS = ["http://your-frontend-url.com"] # Example for production

# --- Application Setup ---
os.environ["COQUI_TOS_AGREED"] = "1"
app = FastAPI(title="TTS Voice Generation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- TTS Model Loading ---
tts_model = None
try:
    use_gpu = torch.cuda.is_available()
    logger.info(f"CUDA available: {use_gpu}")
    logger.info(f"Loading TTS model: {MODEL_NAME}...")
    # Removed safe_globals wrapper
    tts_model = TTS(model_name=MODEL_NAME, gpu=use_gpu)
    logger.info("TTS model loaded successfully.")
except Exception as e:
    logger.error(f"FATAL: Failed to load TTS model: {e}")
    logger.error(traceback.format_exc())
    # Depending on requirements, you might exit here or let the app run without TTS functionality
    # raise RuntimeError(f"Failed to load TTS model: {e}") # Option to stop startup

# Create directories
os.makedirs(VOICES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
logger.info(f"Ensured directories exist: {VOICES_DIR}, {OUTPUTS_DIR}")

# --- API Endpoints ---

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "tts_model_loaded": tts_model is not None}

@app.post("/record_voice")
async def record_voice(audio: UploadFile, user_id: str = Form(...)):
    """Records (saves) a user's voice sample as a WAV file."""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id form field is required.")
    if not audio or not audio.filename:
         raise HTTPException(status_code=400, detail="Audio file upload is required.")

    # Use a unique temporary filename
    temp_suffix = os.path.splitext(audio.filename)[1] if '.' in audio.filename else '.tmp'
    temp_path = os.path.join(VOICES_DIR, f"temp_{user_id}_{int(time.time())}{temp_suffix}")
    voice_path = os.path.join(VOICES_DIR, f"{user_id}.wav")

    try:
        logger.info(f"Receiving voice for user_id: {user_id}, filename: {audio.filename}")
        # Save uploaded file temporarily
        audio_bytes = await audio.read()
        with open(temp_path, "wb") as f:
            f.write(audio_bytes)
        logger.info(f"Temporary file saved: {temp_path}")

        # Convert to WAV using pydub (requires ffmpeg)
        logger.info(f"Converting {temp_path} to WAV format at {voice_path}")
        sound = AudioSegment.from_file(temp_path)
        sound.export(voice_path, format="wav")
        logger.info(f"Voice saved successfully: {voice_path}")

    except Exception as e:
        logger.error(f"Error processing voice for user_id {user_id}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded voice. Ensure it's a valid audio format (e.g., wav, mp3). Error: {e}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.info(f"Removed temporary file: {temp_path}")
            except OSError as e:
                logger.warning(f"Could not remove temporary file {temp_path}: {e}")

    return {"message": f"Voice successfully saved for user ID: {user_id}"}


@app.post("/speak_caption")
async def generate_voice(user_id: str = Form(...), text: str = Form(...)):
    """Generates speech based on text using a previously recorded voice."""
    if tts_model is None:
        logger.error("TTS model not loaded, cannot generate speech.")
        raise HTTPException(status_code=503, detail="TTS service is unavailable due to model loading issue.")

    if not user_id or not text:
        raise HTTPException(status_code=400, detail="user_id and text form fields are required.")

    voice_path = os.path.join(VOICES_DIR, f"{user_id}.wav")
    if not os.path.exists(voice_path):
        logger.warning(f"Voice sample not found for user_id: {user_id} at path: {voice_path}")
        raise HTTPException(status_code=404, detail=f"Voice sample not found for user ID: {user_id}. Please record voice first using /record_voice.")

    # Generate a somewhat unique filename (consider a more robust method if high concurrency)
    output_filename = f"{user_id}_{abs(hash(text)) % 1000000}_out.wav"
    output_path = os.path.join(OUTPUTS_DIR, output_filename)

    try:
        logger.info(f"Generating speech for user_id: {user_id}, text: '{text[:60]}...'")
        start_time = time.time()
        # Ensure speaker_wav path is correct
        tts_model.tts_to_file(
            text=text,
            speaker_wav=voice_path, # Pass the path to the user's voice sample
            language="en", # Make dynamic if supporting multiple languages
            file_path=output_path
        )
        end_time = time.time()
        logger.info(f"Speech generated successfully: {output_path} (took {end_time - start_time:.2f}s)")

        return FileResponse(
            output_path,
            media_type="audio/wav",
            filename=output_filename, # Provide filename for download
            # headers={"Content-Disposition": "inline"} # 'inline' tries to play in browser
        )
    except Exception as e:
        logger.error(f"Error during TTS generation for user_id {user_id}: {e}")
        logger.error(traceback.format_exc())
        # Clean up potentially incomplete output file
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError as rm_err:
                 logger.warning(f"Could not remove failed output file {output_path}: {rm_err}")
        raise HTTPException(status_code=500, detail=f"Failed to generate speech. Error: {e}")

# --- Local Development Runner ---
# This block is NOT executed when running via the Docker CMD
if __name__ == "__main__":
    logger.info("Starting Uvicorn server for local development...")
    # Match the port from Dockerfile CMD for consistency
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)