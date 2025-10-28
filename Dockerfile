FROM ollama/ollama:latest

# Install additional tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Pre-download models (optional)
# RUN ollama pull llama3.2

EXPOSE 11434

CMD ["ollama", "serve"]