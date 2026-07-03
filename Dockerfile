# Stage 1: Build the optimized Rust executable
FROM rust:1.75-slim AS builder

RUN apt-get update && apt-get install -y git libsndfile1-dev pkg-config build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Clone the native low-footprint implementation of the model
RUN git clone https://github.com/kyutai-labs/pocket-tts.git .

# Build the production release artifact
RUN cargo build --release -p pocket-tts-cli

# Stage 2: Minimal runtime footprint execution layer
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y libsndfile1 ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy executable from builder
COPY --from=builder /usr/src/app/target/release/pocket-tts /usr/local/bin/pocket-tts

# Copy local repository files (handles your HTML and custom voice sample)
COPY . /app

EXPOSE 10000

# Start the native HTTP engine natively using less than 100MB of RAM
CMD ["pocket-tts", "serve", "--host", "0.0.0.0", "--port", "10000", "--voice", "my-voice.wav"]
