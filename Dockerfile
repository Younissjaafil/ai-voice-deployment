# # # Stage 1: Builder
# # # Use the same base image, give this stage a name "builder"
# # FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime AS builder

# # # Set working directory for this stage
# # WORKDIR /install_stage

# # # Install build-time system dependencies needed for compiling Python packages
# # # Only install build-essential and git here
# # RUN apt-get update && apt-get install -y --no-install-recommends \
# #     git \
# #     build-essential \
# #     && apt-get clean && rm -rf /var/lib/apt/lists/*

# # # Create a virtual environment in /opt/venv
# # RUN python3 -m venv /opt/venv
# # # Activate venv for subsequent RUN commands in this stage
# # ENV PATH="/opt/venv/bin:$PATH"

# # # Upgrade pip and install wheel (good practice)
# # RUN pip install --upgrade pip wheel

# # # Copy your requirements file into this stage
# # COPY requirements.txt .

# # # Install Python dependencies from requirements.txt into the virtual environment
# # # IMPORTANT: Make sure requirements.txt lists FastAPI, Uvicorn, TTS, etc.,
# # # but DOES NOT include 'torch' or 'pytorch' as it's already in the base image.
# # RUN pip install --no-cache-dir -r requirements.txt

# # # --- End of Builder Stage ---

# # # Stage 2: Runtime
# # # Start from the same clean base image
# # FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# # # Set the final working directory for the application
# # WORKDIR /app

# # # Install only essential RUNTIME system dependencies
# # # No build-essential or git needed here anymore
# # RUN apt-get update && apt-get install -y --no-install-recommends \
# #     ffmpeg \
# #     libsndfile1 \
# #     && apt-get clean && rm -rf /var/lib/apt/lists/*

# # # Copy the virtual environment (with installed packages) from the builder stage
# # COPY --from=builder /opt/venv /opt/venv

# # # Copy your application code (main.py, etc.) into the final image
# # COPY . .

# # # Set environment variable for TTS model cache location
# # # TTS library usually defaults to ~/.local/share/tts or respects XDG_DATA_HOME
# # # Setting XDG_DATA_HOME ensures models are cached inside the container's /app/.local
# # ENV XDG_DATA_HOME=/app/.local
# # # Create the directory just in case the application expects it
# # RUN mkdir -p /app/.local/share/tts

# # # Activate the virtual environment for the final command by adding it to PATH
# # ENV PATH="/opt/venv/bin:$PATH"

# # # Expose the port your FastAPI app runs on
# # EXPOSE 8000

# # # Define the command to run your application using the python from the venv
# # CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# # Stage 1: Builder
# # Use the PyTorch base image with CUDA support
# # Stage 1: Builder
# # Use the PyTorch base image with CUDA support
# FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime AS builder

# WORKDIR /install_stage

# # Install build-time system dependencies (git might be needed by TTS for some models)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     git \
#     build-essential \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

# # Create and activate a virtual environment
# RUN python3 -m venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"

# # Upgrade pip and install wheel
# RUN pip install --upgrade pip wheel

# # Copy requirements file
# COPY requirements.txt .

# # Install Python dependencies from requirements.txt into the virtual environment
# # Excludes torch/torchaudio as they are in the base image.
# RUN pip install --no-cache-dir -r requirements.txt

# # --- End of Builder Stage ---

# # Stage 2: Runtime
# # Start from the same clean base image
# FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# WORKDIR /app

# # Install essential RUNTIME system dependencies
# # ffmpeg needed for pydub, libsndfile1 often needed for audio processing
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     ffmpeg \
#     libsndfile1 \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

# # Copy the virtual environment (with installed packages) from the builder stage
# COPY --from=builder /opt/venv /opt/venv

# # Set environment variable for TTS model cache location within the container
# ENV XDG_DATA_HOME=/app/.local
# # Create the directory structure TTS expects
# RUN mkdir -p /app/.local/share/tts

# # Copy application code AFTER setting up dependencies and cache dirs
# COPY main.py .
# COPY download_model.py .  

# # Activate the virtual environment for subsequent RUN/CMD commands
# ENV PATH="/opt/venv/bin:$PATH"

# # --- Pre-download TTS Model ---
# # Run the download script to cache the model during build time.
# # This significantly reduces cold start time for the serverless function.
# # Ensure COQUI_TOS_AGREED is set if needed by the script/library during build.
# ENV COQUI_TOS_AGREED=1
# RUN python download_model.py

# # Copy remaining application assets (if any, e.g., static files)
# # COPY ./static ./static

# # Ensure the output directories exist (though main.py also creates them)
# RUN mkdir -p /app/voices /app/outputs

# # Expose the port FastAPI runs on
# EXPOSE 8000

# # Define the command to run your application using uvicorn
# # Use the python from the venv. --host 0.0.0.0 makes it accessible externally.
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
# Use --compile to potentially speed up startup
RUN pip install --no-cache-dir --compile -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY main.py .

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable (optional, can be useful)
ENV MODULE_NAME="main"
ENV VARIABLE_NAME="app"

# Run uvicorn server when the container launches
# Use 0.0.0.0 to make it accessible from outside the container
# Use port 80 as exposed
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]