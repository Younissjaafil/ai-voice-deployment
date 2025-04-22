# download_model.py
import os
import torch
from TTS.api import TTS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure env var is set for the script
os.environ["COQUI_TOS_AGREED"] = "1"

TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
CACHE_PATH = "/app/.local/share/tts" # Match Dockerfile XDG_DATA_HOME

logger.info("--- Starting TTS Model Download ---")
logger.info(f"Model to download: {TTS_MODEL}")
logger.info(f"Target cache directory: {CACHE_PATH}")

# Create the target directory just in case
os.makedirs(CACHE_PATH, exist_ok=True)
os.environ['XDG_DATA_HOME'] = '/app/.local' # Explicitly set for this script

try:
    # Initialize TTS. Set gpu=False as GPU is likely not available during build.
    # This initialization triggers the download process.
    tts = TTS(model_name=TTS_MODEL, gpu=False)
    logger.info("--- TTS model download/verification complete. ---")
    # You could add a small test synthesis here if desired, but it adds build time
    # tts.tts_to_file(text="Model download successful.", file_path="/tmp/test.wav")
    # logger.info("Test synthesis successful.")
except Exception as e:
    logger.error(f"--- Error downloading TTS model: {e} ---", exc_info=True)
    # Exit with a non-zero code to potentially fail the build if download fails
    exit(1)

logger.info("--- Model download script finished. ---")