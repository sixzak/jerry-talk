FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg git wget && rm -rf /var/lib/apt/lists/*

# Pulls the official OpenVoice project code directly into your server
RUN git clone https://github.com .

RUN pip install -e .
RUN pip install fastapi uvicorn pydantic

RUN mkdir -p checkpoints/converter

# Pulls the official audio converter files into your server
RUN wget -O checkpoints/converter/checkpoint.pth https://github.com
RUN wget -O checkpoints/converter/config.json https://github.com

COPY reference_speaker.wav .
COPY main.py .

CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "10000"]
