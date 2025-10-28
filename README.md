# 🤖 LLM Inference - Local Language Models with Ollama

<div align="center">

![LLM](https://img.shields.io/badge/Ollama-LLM_Inference-FF6F00?style=for-the-badge)
![Performance](https://img.shields.io/badge/Performance-50+_tokens/sec-success?style=for-the-badge)

**Run powerful language models entirely on your Jetson Thor**

[Quick Deploy](#-quick-deploy) • [Models](#-supported-models) • [API Usage](#-api-usage)

</div>

---

## 📋 Overview

Run state-of-the-art language models like Llama 3.2, Mistral, and Gemma locally on your Jetson Thor. Perfect for:

- 💬 **Chatbots** - Build privacy-first conversational AI
- 📝 **Content Generation** - Create articles, code, summaries
- 🔍 **Text Analysis** - Sentiment analysis, classification
- 🌐 **Translation** - Multi-language support
- 🤝 **Assistant Applications** - Personal AI helper

### Key Features

✨ **50+ Tokens/Second** - Fast inference with quantization
🔒 **100% Private** - All data stays on device
🎯 **Multiple Models** - Llama, Mistral, Gemma, Phi, and more
⚡ **Low Latency** - < 100ms response time
🌐 **OpenAI Compatible API** - Drop-in replacement
💾 **Model Management** - Easy download and switching

---

## ⚡ Quick Deploy

```bash
# Clone and navigate
git clone https://github.com/Raveendiran-RR/Nvidia-AGX-Jetson-Thor-Docker-AI-Lab.git
cd Nvidia-AGX-Jetson-Thor-Docker-AI-Lab
git checkout use-case/llm-inference

# Deploy Ollama
docker-compose up -d

# Pull a model (e.g., Llama 3.2)
docker exec ollama ollama pull llama3.2

# Test the model
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?"
}'
```

**Access Points:**
- API: http://jetson-thor.local:11434
- Web UI: http://jetson-thor.local:3000

---

## 🎯 Supported Models

| Model | Size | RAM | Performance | Use Case |
|-------|------|-----|-------------|----------|
| **Llama 3.2 1B** | 1.3GB | 2GB | 80 tok/s | Chat, Code |
| **Llama 3.2 3B** | 2GB | 4GB | 60 tok/s | General purpose |
| **Mistral 7B** | 4.1GB | 8GB | 45 tok/s | Advanced chat |
| **Phi-3 Mini** | 2.2GB | 4GB | 65 tok/s | Lightweight |
| **Gemma 2B** | 1.7GB | 3GB | 70 tok/s | Google's model |
| **CodeLlama 7B** | 3.8GB | 8GB | 40 tok/s | Code generation |

---

## 💻 Usage Examples

### Chat Completion

```python
import requests

response = requests.post('http://localhost:11434/api/chat', json={
    "model": "llama3.2",
    "messages": [
        {"role": "user", "content": "Explain quantum computing"}
    ]
})

print(response.json()['message']['content'])
```

### Streaming Response

```python
import requests

with requests.post('http://localhost:11434/api/generate', 
                   json={"model": "llama3.2", "prompt": "Write a story"},
                   stream=True) as r:
    for line in r.iter_lines():
        if line:
            print(json.loads(line)['response'], end='')
```

### OpenAI Compatible

```python
from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'  # required but unused
)

response = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

---

## 📊 Performance Benchmarks

**Llama 3.2 1B** (Recommended for Jetson)
- Tokens/sec: 80
- First token latency: 50ms
- RAM usage: 2.5GB
- Power: 35W

**Mistral 7B** (Advanced use)
- Tokens/sec: 45
- First token latency: 100ms
- RAM usage: 8GB
- Power: 55W

---

## 🛠️ Configuration

### Environment Variables

```yaml
# Model settings
OLLAMA_MODEL=llama3.2
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=2

# Performance
OLLAMA_NUM_GPU=1
OLLAMA_GPU_OVERHEAD=500M

# Context
OLLAMA_NUM_CTX=4096
OLLAMA_NUM_BATCH=512
```

---

[🏠 Main Repository](../../) | [📖 Setup Guide](../../SETUP.md)

</div>