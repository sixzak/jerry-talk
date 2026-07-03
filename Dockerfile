FROM python:3.10-slim

# Install system utilities necessary for media pipelines
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ensure PyTorch CPU wheels install smoothly before layering logic packages
RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir omnivoice fastapi uvicorn pydub groq pydantic soundfile

COPY . .

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
