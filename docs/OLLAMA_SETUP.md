# Ollama Setup Guide

This guide will help you set up Ollama and configure the AI Chess Learning Platform to use local LLMs.

## What is Ollama?

Ollama is a tool that lets you run large language models (LLMs) locally on your computer. Think of it as running ChatGPT, but:
- **100% private**: No data sent to external servers
- **Free**: No API costs or subscriptions
- **Fast**: Direct access to your GPU/CPU
- **Offline**: Works without internet after initial model download

## Installation

### macOS

```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

### Linux

```bash
# Download and install
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama  # Auto-start on boot

# Verify
ollama --version
```

### Windows

1. Download the installer from [ollama.ai](https://ollama.ai/download)
2. Run the `.exe` file and follow the installation wizard
3. Open Command Prompt and verify: `ollama --version`

## Downloading Models

### Recommended Models for Chess Learning

#### 1. Llama 3 (Default - Best Balance)
```bash
ollama pull llama3
```
- **Size**: ~4.7 GB
- **RAM Required**: 8 GB
- **Best for**: Detailed explanations, conversational teaching
- **Speed**: Medium
- **Quality**: Excellent

#### 2. Mistral (Fast Alternative)
```bash
ollama pull mistral
```
- **Size**: ~4.1 GB
- **RAM Required**: 8 GB
- **Best for**: Quick responses, efficient chat
- **Speed**: Fast
- **Quality**: Very Good

#### 3. Phi-3 (Lightweight)
```bash
ollama pull phi3
```
- **Size**: ~2.3 GB
- **RAM Required**: 4 GB
- **Best for**: Low-resource systems, rapid interactions
- **Speed**: Very Fast
- **Quality**: Good

#### 4. Qwen2 (Multilingual)
```bash
ollama pull qwen2
```
- **Size**: ~4.4 GB
- **RAM Required**: 8 GB
- **Best for**: Non-English languages, international users
- **Speed**: Medium
- **Quality**: Very Good

### Choosing the Right Model

| If you have... | Use this model |
|----------------|----------------|
| 16+ GB RAM, want best quality | `llama3` or `llama3:70b` (if 32GB+ RAM) |
| 8-16 GB RAM, need good balance | `llama3` or `mistral` |
| 4-8 GB RAM, prioritize speed | `phi3` |
| Need multilingual support | `qwen2` |
| Want to experiment | Try multiple! |

## Configuration

### 1. Start Ollama Server

```bash
# Start the Ollama service (keeps running in background)
ollama serve
```

**Important**: The Ollama server must be running whenever you use the chess platform.

### 2. Test Your Installation

```bash
# Interactive chat test
ollama run llama3

# Ask it a chess question
>>> Explain why controlling the center is important in chess
```

Press `Ctrl+D` or type `/bye` to exit.

### 3. Configure the Chess Platform

Edit your backend `.env` file:

```bash
cd /workspaces/AIChessBot/backend
cp .env.example .env
```

Then set these values:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Alternative models:
# OLLAMA_MODEL=mistral
# OLLAMA_MODEL=phi3
# OLLAMA_MODEL=qwen2
```

### 4. Verify Connection

Start your backend server:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Check the health endpoint:
```bash
curl http://localhost:8000/api/llm/status
```

Expected response:
```json
{
  "connected": true,
  "base_url": "http://localhost:11434",
  "model": "llama3",
  "status": "operational"
}
```

## Advanced Configuration

### GPU Acceleration

Ollama automatically uses your GPU if available:
- **NVIDIA**: CUDA support (RTX, GTX series)
- **Apple Silicon**: Metal acceleration (M1, M2, M3)
- **AMD**: ROCm support (Linux only)

Check GPU usage:
```bash
# NVIDIA
nvidia-smi

# Apple Silicon
# Check Activity Monitor > GPU tab
```

### Custom Model Parameters

You can fine-tune model behavior in `backend/app/services/ollama_service.py`:

```python
# Example: Adjust temperature for different personas
"grandmaster": {
    "temperature": 0.3,  # Lower = more deterministic/analytical
    ...
},
"friendly_teacher": {
    "temperature": 0.7,  # Medium = balanced creativity
    ...
},
"aggressive_rival": {
    "temperature": 0.9,  # Higher = more creative/varied
    ...
}
```

### Running Multiple Models

You can switch models on-the-fly:

```bash
# Download multiple models
ollama pull llama3
ollama pull mistral
ollama pull phi3

# List installed models
ollama list
```

Change model in `.env`:
```env
OLLAMA_MODEL=mistral
```

Restart your backend server for changes to take effect.

## Troubleshooting

### Ollama Not Found

**Problem**: `command not found: ollama`

**Solution**:
```bash
# Reinstall Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Add to PATH (Linux/macOS)
export PATH=$PATH:/usr/local/bin
```

### Model Download Fails

**Problem**: Network error during `ollama pull`

**Solutions**:
1. Check internet connection
2. Try smaller model first: `ollama pull phi3`
3. Resume interrupted download: Run same `pull` command again

### Service Won't Start

**Problem**: `Error: could not connect to ollama server`

**Solution**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start manually
ollama serve

# Or as systemd service (Linux)
sudo systemctl start ollama
sudo systemctl status ollama
```

### Out of Memory

**Problem**: System freezes or crashes when running model

**Solutions**:
1. Use lighter model: `phi3` instead of `llama3`
2. Close other applications
3. Reduce `max_tokens` in API requests
4. Use quantized models: `ollama pull llama3:7b-q4_0`

### Slow Responses

**Problem**: LLM takes 10+ seconds to respond

**Solutions**:
1. **Use GPU**: Ensure CUDA/Metal is working
2. **Smaller model**: Switch to `mistral` or `phi3`
3. **Reduce context**: Shorten prompts
4. **Quantized model**: `ollama pull llama3:7b-q4_0` (faster, slight quality loss)

## Performance Benchmarks

Approximate response times on different hardware:

| Hardware | Llama 3 | Mistral | Phi-3 |
|----------|---------|---------|-------|
| M1 Mac (8GB) | 2-4s | 1-3s | 0.5-1s |
| RTX 3060 (12GB) | 1-2s | 0.5-1s | 0.3-0.5s |
| CPU-only (16GB) | 8-15s | 5-10s | 2-4s |

## Best Practices

1. **Keep Ollama running**: Start `ollama serve` at system boot
2. **Update regularly**: `ollama pull <model>` to get latest versions
3. **Test models**: Try different models to find your preference
4. **Monitor resources**: Use `htop` or Activity Monitor during use
5. **Backup configs**: Save your `.env` and persona customizations

## Switching Personas

The platform includes three AI personas, all powered by your chosen Ollama model:

1. **The Grandmaster**: Analytical, technical, demanding
2. **Friendly Teacher**: Patient, encouraging, explanatory
3. **Aggressive Rival**: Competitive, playful, energetic

Same model, different prompts! Change persona in the frontend UI or via API:

```bash
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Why is 1.e4 popular?",
    "persona": "grandmaster"
  }'
```

## Getting Help

- **Ollama Docs**: https://github.com/ollama/ollama
- **Model Library**: https://ollama.ai/library
- **Discord Community**: https://discord.gg/ollama
- **Chess Platform Issues**: GitHub Issues on this repo

## Next Steps

After Ollama is configured:
1. ✅ Install Stockfish: See [DEPLOYMENT.md](./DEPLOYMENT.md)
2. ✅ Start the backend: `uvicorn app.main:app --reload`
3. ✅ Launch the frontend: `npm run dev`
4. ✅ Play your first AI-coached game!

---

**Pro Tip**: Run `ollama list` periodically to see which models you have installed and their sizes. Delete unused models with `ollama rm <model>` to free up disk space.
