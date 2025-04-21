# 🗣️ XTTS Voice Cloning API Setup (GPU Version)

This guide provides step-by-step instructions to install and run a FastAPI-based XTTS voice cloning API using a Python virtual environment. This setup is intended to run **on a GPU-enabled environment**.

---

## 🔧 Requirements

- Python **3.10** or **3.11**
- A machine with **CUDA-compatible GPU**
- `git`, `ffmpeg`, and `virtualenv` installed

---

## 📦 1. Create and Activate Virtual Environment

```bash
python -m venv venv
```

Activate it:

- **Windows**:

  ```bash
  venv\Scripts\activate
  ```

- **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```

---

## 📥 2. Upgrade Pip and Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install torch==2.2.0
pip install pydub==0.25.1
pip install TTS==0.17.2
pip install fastapi==0.104.1
pip install uvicorn==0.23.2
```

---

## ⚠️ 3. Accept Coqui License Terms

Before running, you must accept the Coqui TTS Terms of Service:

```bash
# Linux/macOS
export COQUI_TOS_AGREED=1

# Windows CMD
set COQUI_TOS_AGREED=1
```

Alternatively, add this to your Python script:

```python
import os
os.environ["COQUI_TOS_AGREED"] = "1"
```

---

## 🧠 4. Safe Globals (Required for Loading the Model)

Make sure to load the model like this in your `app.py`:

```python
from TTS.api import TTS
from torch.serialization import safe_globals
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

with safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig]):
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
```

---

## 🚀 5. Run the FastAPI App

To launch the server on `localhost:8000`:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Replace `app:app` with your actual filename and FastAPI instance name.

---

## 📁 6. Optional Tools

Install these if you're handling file uploads:

```bash
pip install python-multipart aiofiles
```

---

## ✅ Final Checklist

- [ ] Python 3.10 or 3.11 installed
- [ ] Virtual environment created and activated
- [ ] All required packages installed
- [ ] Coqui ToS agreed (`COQUI_TOS_AGREED=1`)
- [ ] GPU is available and detected by PyTorch (`torch.cuda.is_available()` returns `True`)
- [ ] FastAPI server runs successfully

---

**Note:** Model is around 1.5 GB and will be downloaded automatically on first run. You can cache it manually in `.local/share/tts/`.
