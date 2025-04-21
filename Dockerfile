FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# Install system-level dependencies
RUN apt-get update && \
    apt-get install -y python3-distutils git ffmpeg && \
    apt-get clean

# Set workdir
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install core Python packages first to avoid conflicts
RUN pip install --upgrade pip && \
    pip install --no-cache-dir numpy==1.22.0

# Then install rest
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of your app
COPY . .

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
