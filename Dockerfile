# YOLOv8 Computer Vision - NVIDIA Jetson Thor
# Optimized for ARM64 architecture with GPU acceleration

FROM nvcr.io/nvidia/l4t-pytorch:r36.2.0-pth2.1-py3

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libopencv-dev \
    python3-opencv \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    v4l-utils \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip setuptools wheel

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install YOLOv8 with TensorRT support
RUN pip3 install --no-cache-dir \
    ultralytics==8.1.0 \
    torch-tensorrt \
    onnx \
    onnxruntime-gpu

# Copy application files
COPY app.py .
COPY config.yaml .
COPY utils/ ./utils/
COPY static/ ./static/
COPY templates/ ./templates/

# Create directories for models and output
RUN mkdir -p /models /output /videos

# Download YOLOv8 models
RUN python3 -c "from ultralytics import YOLO; \
    YOLO('yolov8n.pt'); \
    YOLO('yolov8s.pt')"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_NAME=yolov8n
ENV CONFIDENCE=0.25
ENV VIDEO_SOURCE=0
ENV RESOLUTION=1920x1080
ENV USE_TENSORRT=true
ENV USE_FP16=true

# Expose port for web interface
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python3", "app.py"]