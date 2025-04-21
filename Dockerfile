FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

WORKDIR /app
COPY . .

# Fixes for build dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    python3-distutils \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Python deps
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    numpy==1.22.0 \
    torch==2.2.0 \
    torchaudio==2.2.0 && \
    pip install --no-cache-dir \
    TTS==0.17.2 \
    fastapi \
    uvicorn \
    pydub \
    Pillow

EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
