# # Use PyTorch runtime with CUDA support
# FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# # Set working directory
# WORKDIR /app

# # Copy and install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy your application code
# COPY . .

# # Agree to Coqui TTS terms
# ENV COQUI_TOS_AGREED=1

# # Expose FastAPI port
# EXPOSE 8000

# # Launch the API
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3-distutils git ffmpeg && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir numpy==1.22.0 && \
    pip install --no-cache-dir --no-build-isolation -r requirements.txt

# Copy application code
COPY . .

# Set default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
