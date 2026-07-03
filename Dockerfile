FROM python:3.10-slim

# Install necessary system-level compilation and audio codecs
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all local repository files into the docker image
COPY . /app

# Install lightweight CPU-optimized PyTorch and dependencies
RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir pocket-tts fastapi uvicorn scipy

EXPOSE 10000

# Fire up the production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
