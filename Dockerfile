# FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# # Install system-level dependencies
# RUN apt-get update && \
#     apt-get install -y python3-distutils git ffmpeg && \
#     apt-get clean

# # Set workdir
# WORKDIR /app

# # Copy requirements first
# COPY requirements.txt .

# # Install core Python packages first to avoid conflicts
# RUN pip install --upgrade pip && \
#     pip install --no-cache-dir numpy==1.22.0

# # Then install rest
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy rest of your app
# COPY . .

# # Start command
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Set environment variable to auto-accept Coqui terms
ENV COQUI_TOS_AGREED=1

# Install required dependencies
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 git \
    && pip install --upgrade pip \
    && pip install --no-cache-dir fastapi uvicorn pydub Pillow \
    && pip install --no-cache-dir TTS==0.17.2 torch==2.2.0 torchaudio==2.2.0

# Optional: Download English model (e.g., `tts_models/en/ljspeech/tacotron2-DDC`)
RUN python3 -c "from TTS.utils.manage import ModelManager; ModelManager().download_model('tts_models/en/ljspeech/tacotron2-DDC')"

# Expose port
EXPOSE 7860

# Start API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
