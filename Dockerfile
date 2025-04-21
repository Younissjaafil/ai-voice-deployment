# Use PyTorch runtime with CUDA support
FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Agree to Coqui TTS terms
ENV COQUI_TOS_AGREED=1

# Expose FastAPI port
EXPOSE 8000

# Launch the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
