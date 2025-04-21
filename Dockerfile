# Stage 1: Builder
# Use the same base image, give this stage a name "builder"
FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime AS builder

# Set working directory for this stage
WORKDIR /install_stage

# Install build-time system dependencies needed for compiling Python packages
# Only install build-essential and git here
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a virtual environment in /opt/venv
RUN python3 -m venv /opt/venv
# Activate venv for subsequent RUN commands in this stage
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install wheel (good practice)
RUN pip install --upgrade pip wheel

# Copy your requirements file into this stage
COPY requirements.txt .

# Install Python dependencies from requirements.txt into the virtual environment
# IMPORTANT: Make sure requirements.txt lists FastAPI, Uvicorn, TTS, etc.,
# but DOES NOT include 'torch' or 'pytorch' as it's already in the base image.
RUN pip install --no-cache-dir -r requirements.txt

# --- End of Builder Stage ---

# Stage 2: Runtime
# Start from the same clean base image
FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# Set the final working directory for the application
WORKDIR /app

# Install only essential RUNTIME system dependencies
# No build-essential or git needed here anymore
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment (with installed packages) from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy your application code (main.py, etc.) into the final image
COPY . .

# Set environment variable for TTS model cache location
# TTS library usually defaults to ~/.local/share/tts or respects XDG_DATA_HOME
# Setting XDG_DATA_HOME ensures models are cached inside the container's /app/.local
ENV XDG_DATA_HOME=/app/.local
# Create the directory just in case the application expects it
RUN mkdir -p /app/.local/share/tts

# Activate the virtual environment for the final command by adding it to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Define the command to run your application using the python from the venv
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]