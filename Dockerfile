# FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# WORKDIR /app
# COPY . .

# # Install required system packages
# RUN apt-get update && apt-get install -y \
#     ffmpeg \
#     libsndfile1 \
#     git \
#     python3-distutils \
#     build-essential \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

# # Python dependencies (numpy must match TTS)
# RUN pip install --upgrade pip && \
#     pip install --no-cache-dir \
#     numpy==1.22.0 \
#     torch==2.2.0 \
#     torchaudio==2.2.0 && \
#     pip install --no-cache-dir \
#     TTS==0.17.2 \
#     fastapi \
#     uvicorn \
#     pydub \
#     Pillow

# EXPOSE 7860

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
# Use the specified PyTorch base image
FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

WORKDIR /app
COPY . .

# Set TTS_HOME environment variable to cache models inside the app directory
# Or map this path to persistent storage on Runpod if preferred (e.g., /workspace/.tts_cache)
ENV TTS_HOME=/app/.local/share/tts
RUN mkdir -p $TTS_HOME

# Install required system packages
# Added --no-install-recommends, removed python3-distutils
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Removed explicit numpy version, install TTS and other libs first
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    TTS==0.17.2 \
    fastapi \
    uvicorn \
    pydub \
    Pillow && \
    # Install torch/torchaudio matching the base image *after* other deps
    pip install --no-cache-dir \
    torch==2.2.0 \
    torchaudio==2.2.0

# --- Optional: Pre-download model during build ---
# This increases image size significantly but improves runtime reliability.
# Use gpu=False if your build environment doesn't have a GPU.
# Uncomment the following line to enable pre-downloading:
# RUN python -c "from TTS.api import TTS; print('Downloading TTS model...'); TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2', gpu=False); print('Model download complete.')"
# -------------------------------------------------

EXPOSE 7860

# Command to run the application using Uvicorn (matches EXPOSE)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]