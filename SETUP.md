# 📦 Complete Setup Guide: NVIDIA AGX Jetson Thor

<div align="center">

**From Unboxing to Your First AI Deployment**

*Estimated Time: 30-60 minutes*

</div>

---

## 📑 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Hardware Setup](#-hardware-setup)
3. [JetPack Installation](#-jetpack-installation)
4. [Docker Installation](#-docker-installation)
5. [NVIDIA Container Runtime](#-nvidia-container-runtime-setup)
6. [Verification](#-verification)
7. [Post-Installation Optimization](#-post-installation-optimization)
8. [Common Pitfalls](#-common-pitfalls-and-solutions)

---

## ✅ Prerequisites

Before you begin, ensure you have:

### Hardware Checklist
- [ ] NVIDIA AGX Jetson Thor developer kit
- [ ] USB-C Power Delivery adapter (65W or higher)
- [ ] Ethernet cable (recommended for initial setup)
- [ ] MicroSD card or NVMe SSD (500GB+ recommended)
- [ ] USB keyboard and mouse
- [ ] HDMI/DisplayPort monitor
- [ ] Host computer (for flashing JetPack)

### Software Checklist
- [ ] Ubuntu 18.04/20.04/22.04 host machine (for SDK Manager)
- [ ] NVIDIA Developer account (free)
- [ ] Stable internet connection (10+ Mbps)
- [ ] At least 50GB free disk space on host

---

## 🔌 Hardware Setup

### Step 1: Unboxing and Physical Assembly

```
┌──────────────────────────────────────────────┐
│  1. Remove Jetson Thor from packaging        │
│  2. Attach heatsink/cooling solution          │
│  3. Insert NVMe SSD (if using)               │
│  4. Connect power supply                      │
│  5. Connect Ethernet cable                    │
│  6. Connect monitor via HDMI/DisplayPort     │
│  7. Connect keyboard and mouse               │
└──────────────────────────────────────────────┘
```

### Step 2: Power On First Time

1. **Connect power adapter** to the USB-C port
2. **Press the power button** (usually located on the side)
3. **Wait for boot** (first boot may take 2-3 minutes)
4. **LED indicators** should light up green

> ⚠️ **Important**: Do not disconnect power during first boot

---

## 💿 JetPack Installation

JetPack SDK is NVIDIA's comprehensive development environment for Jetson platforms.

### Method 1: SDK Manager (Recommended)

#### On Your Host Computer:

**Step 1: Install SDK Manager**
```bash
# Download SDK Manager from NVIDIA Developer Portal
wget https://developer.nvidia.com/downloads/sdkmanager_2.1.0-11682_amd64.deb

# Install SDK Manager
sudo dpkg -i sdkmanager_2.1.0-11682_amd64.deb
sudo apt-get install -f
```

**Step 2: Launch SDK Manager**
```bash
sdkmanager
```

**Step 3: Configure Installation**
1. **Login** with your NVIDIA Developer account
2. **Select hardware**: AGX Jetson Thor
3. **Select JetPack version**: 6.0 or later
4. **Target components**:
   - ✅ Jetson Linux
   - ✅ CUDA Toolkit
   - ✅ cuDNN
   - ✅ TensorRT
   - ✅ VPI (Vision Programming Interface)
   - ✅ OpenCV
   - ✅ Docker
5. **Click Continue**

**Step 4: Put Jetson Thor in Recovery Mode**
1. Power off Jetson Thor
2. Connect USB-C cable between host and Jetson
3. Hold **Recovery button** (REC)
4. Press **Power button**
5. Release **Recovery button** after 2 seconds

**Step 5: Verify Recovery Mode**
```bash
# On host computer
lsusb | grep -i nvidia

# Should output something like:
# Bus 001 Device 005: ID 0955:7023 NVIDIA Corp. Jetson Thor [recovery mode]
```

**Step 6: Flash JetPack**
- SDK Manager will automatically detect the device
- Click **Install** and wait (30-60 minutes)
- Monitor progress on screen

### Method 2: SD Card Image (Alternative)

**Download and Flash Image:**
```bash
# Download JetPack image
wget https://developer.nvidia.com/jetpack-60-thor-image.zip

# Extract image
unzip jetpack-60-thor-image.zip

# Flash to SD card (replace /dev/sdX with your SD card)
sudo dd if=jetpack-60-thor.img of=/dev/sdX bs=4M status=progress
sync
```

### Post-Installation Configuration

**First Boot Setup:**
```bash
# Set timezone
sudo timedatectl set-timezone America/New_York

# Update system
sudo apt update && sudo apt upgrade -y

# Set maximum performance mode
sudo nvpmodel -m 0
sudo jetson_clocks

# Verify JetPack installation
sudo apt-cache show nvidia-jetpack
```

---

## 🐳 Docker Installation

Docker is essential for containerized AI workloads.

### Step 1: Install Docker Engine

```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo \
  "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
sudo docker --version
```

### Step 2: Configure Docker for Non-Root User

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Verify non-root access
docker ps
```

### Step 3: Configure Docker Daemon

```bash
# Create or edit daemon.json
sudo nano /etc/docker/daemon.json
```

**Add the following configuration:**
```json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  },
  "default-runtime": "nvidia",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "data-root": "/mnt/nvme/docker",
  "storage-driver": "overlay2"
}
```

**Restart Docker:**
```bash
sudo systemctl restart docker
sudo systemctl enable docker

# Verify daemon configuration
docker info | grep -i runtime
```

---

## 🎮 NVIDIA Container Runtime Setup

The NVIDIA Container Runtime enables GPU access within Docker containers.

### Step 1: Install NVIDIA Container Toolkit

```bash
# Configure the repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit nvidia-container-runtime

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker
sudo systemctl restart docker
```

### Step 2: Verify GPU Access

```bash
# Test GPU access in container
docker run --rm --runtime nvidia --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi

# Expected output: NVIDIA GPU information table
```

### Step 3: Test with Sample Container

```bash
# Pull NVIDIA L4T base image
docker pull nvcr.io/nvidia/l4t-base:r36.2.0

# Run with GPU access
docker run -it --rm --runtime nvidia --gpus all \
  nvcr.io/nvidia/l4t-base:r36.2.0 \
  bash -c "nvidia-smi && nvcc --version"
```

---

## ✔️ Verification

Run these commands to verify your setup:

### System Verification

```bash
# Check NVIDIA drivers
nvidia-smi

# Check CUDA installation
nvcc --version

# Check Docker version
docker --version

# Check Docker Compose
docker compose version

# Check NVIDIA runtime
docker info | grep -i nvidia

# Check system resources
tegrastats

# Check JetPack components
dpkg -l | grep nvidia
```

### Performance Verification

```bash
# Set maximum performance
sudo nvpmodel -m 0
sudo jetson_clocks

# Monitor real-time stats
tegrastats

# Expected output:
# RAM 5234/64329MB (lfb 12495x4MB) SWAP 0/32164MB
# CPU [25%@2265,24%@2265,26%@2265,24%@2265,26%@2265,25%@2265,24%@2265,25%@2265]
# GR3D_FREQ 0% GR3D2_FREQ 0%
```

### Docker GPU Test

```bash
# Create test script
cat > test-gpu.py << 'EOF'
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"Device count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"Device name: {torch.cuda.get_device_name(0)}")
    print(f"Device memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
EOF

# Run test in container
docker run --rm --runtime nvidia --gpus all \
  -v $(pwd):/workspace \
  nvcr.io/nvidia/pytorch:24.01-py3 \
  python /workspace/test-gpu.py
```

---

## ⚡ Post-Installation Optimization

### Storage Optimization

```bash
# Move Docker root to NVMe (if applicable)
sudo systemctl stop docker

# Create new Docker root directory
sudo mkdir -p /mnt/nvme/docker

# Update daemon.json with new data-root
sudo nano /etc/docker/daemon.json
# Set "data-root": "/mnt/nvme/docker"

# Copy existing Docker data
sudo rsync -aP /var/lib/docker/ /mnt/nvme/docker/

# Restart Docker
sudo systemctl start docker

# Verify new location
docker info | grep "Docker Root Dir"
```

### Memory Optimization

```bash
# Increase swap space for large models
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify swap
free -h
```

### Network Optimization

```bash
# Optimize TCP settings for AI workloads
sudo tee /etc/sysctl.d/99-jetson-network.conf << EOF
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq
EOF

# Apply settings
sudo sysctl -p /etc/sysctl.d/99-jetson-network.conf
```

### Power Management

```bash
# Create custom power mode script
cat > ~/max-performance.sh << 'EOF'
#!/bin/bash
sudo nvpmodel -m 0
sudo jetson_clocks
echo "Jetson Thor set to maximum performance mode"
tegrastats --interval 1000 --logfile /tmp/tegrastats.log &
EOF

chmod +x ~/max-performance.sh

# Run on startup
echo "@reboot ~/max-performance.sh" | crontab -
```

### Docker Image Optimization

```bash
# Enable Docker buildx for multi-arch builds
docker buildx create --name jetson-builder --use
docker buildx inspect --bootstrap

# Configure image caching
mkdir -p ~/.docker
cat > ~/.docker/config.json << 'EOF'
{
  "experimental": "enabled",
  "features": {
    "buildkit": true
  }
}
EOF
```

---

## 🚨 Common Pitfalls and Solutions

### Issue 1: Docker Daemon Won't Start

**Symptoms:**
```
Failed to start docker.service: Unit docker.service is masked
```

**Solution:**
```bash
sudo systemctl unmask docker
sudo systemctl enable docker
sudo systemctl start docker
```

### Issue 2: GPU Not Detected in Container

**Symptoms:**
```
docker: Error response from daemon: could not select device driver "" with capabilities: [[gpu]]
```

**Solution:**
```bash
# Reinstall NVIDIA Container Runtime
sudo apt-get remove --purge nvidia-container-runtime
sudo apt-get install -y nvidia-container-toolkit

# Reconfigure Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test again
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

### Issue 3: Out of Disk Space

**Symptoms:**
```
no space left on device
```

**Solution:**
```bash
# Clean Docker system
docker system prune -a --volumes -f

# Check disk usage
df -h
docker system df

# Move Docker to NVMe (see Post-Installation Optimization)
```

### Issue 4: Slow Performance

**Symptoms:**
- Low FPS in AI workloads
- High inference latency

**Solution:**
```bash
# Enable maximum performance
sudo nvpmodel -m 0
sudo jetson_clocks

# Check thermal throttling
tegrastats | grep temp

# Verify GPU utilization
nvidia-smi dmon -s u

# If throttling, improve cooling
```

### Issue 5: Container Network Issues

**Symptoms:**
```
Could not resolve host: example.com
```

**Solution:**
```bash
# Update DNS settings
sudo nano /etc/docker/daemon.json
# Add:
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}

# Restart Docker
sudo systemctl restart docker

# Verify connectivity
docker run --rm alpine ping -c 3 google.com
```

### Issue 6: Permission Denied Errors

**Symptoms:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes
newgrp docker

# Logout and login again
# Or reboot system
sudo reboot
```

---

## 🎯 Next Steps

Congratulations! Your Jetson Thor is now fully configured. Here's what to do next:

### 1. Test Your Setup
```bash
# Clone this repository
git clone https://github.com/Raveendiran-RR/Nvidia-AGX-Jetson-Thor-Docker-AI-Lab.git
cd Nvidia-AGX-Jetson-Thor-Docker-AI-Lab

# Run system check
./scripts/check-system.sh
```

### 2. Deploy Your First Use Case
```bash
# Try Computer Vision example
git checkout use-case/computer-vision
docker-compose up -d

# Access at http://jetson-thor.local:8080
```

### 3. Explore Documentation
- [Computer Vision Guide](../../tree/use-case/computer-vision)
- [LLM Inference Guide](../../tree/use-case/llm-inference)
- [Performance Tuning](docs/performance-tuning.md)

### 4. Join the Community
- 💬 [Discord](https://discord.gg/jetson-ai-lab)
- 🐦 [Twitter](https://twitter.com/JetsonAILab)
- 📺 [YouTube Tutorials](https://youtube.com/@JetsonAILab)

---

## 📞 Need Help?

If you encounter issues:
1. Check the [Troubleshooting](#-common-pitfalls-and-solutions) section
2. Search [GitHub Issues](../../issues)
3. Ask in our [Discord community](https://discord.gg/jetson-ai-lab)
4. Create a [new issue](../../issues/new) with detailed logs

**Include in your report:**
```bash
# System information
uname -a
nvidia-smi
docker info
tegrastats
```

---

<div align="center">

**✅ Setup Complete! Ready to build amazing AI applications!**

[🏠 Back to Main README](README.md) | [🚀 Quick Start Guide](README.md#-quick-start-0-to-running-in-30-minutes)

</div>