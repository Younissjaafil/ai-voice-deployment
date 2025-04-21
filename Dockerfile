# Use the specified PyTorch base image
FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

WORKDIR /app
COPY . .

# Set TTS_HOME environment variable to cache models inside the app directory
# Or map this path to persistent storage on Runpod if preferred (e.g., /workspace/.tts_cache)
ENV TTS_HOME=/app/.local/share/tts
RUN mkdir -p $TTS_HOME

# Install required system packages
# (This part seemed okay in the log, keeping it)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- FIX APPLIED HERE ---
# Install Python dependencies
# 1. Removed explicit numpy==1.22.0 pin.
# 2. Install TTS and other libraries *before* torch/torchaudio.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    TTS==0.17.2 \
    fastapi \
    uvicorn \
    pydub \
    Pillow && \
    # Install torch/torchaudio matching the base image *after* other deps
    # This ensures compatibility with the base image's CUDA/CuDNN setup
    pip install --no-cache-dir \
    torch==2.2.0 \
    torchaudio==2.2.0

# --- Optional but Recommended for Runpod Reliability: Pre-download model ---
# This increases image size significantly but prevents download issues/delays at runtime.
# Use gpu=False if your build environment doesn't have a GPU.
# Uncomment the following line to enable pre-downloading:
# RUN python -c "from TTS.api import TTS; print('Downloading TTS model...'); TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2', gpu=False); print('Model download complete.')"
# --------------------------------------------------------------------------

EXPOSE 7860

# Command to run the application using Uvicorn (matches EXPOSE)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]