# 🚀 Provenance Guardian Setup Guide

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **GPU**: NVIDIA GPU with CUDA 12.1+ (recommended) or 16GB+ RAM for CPU
- **Storage**: 50GB+ free space for models

### Required Accounts
- [Hugging Face](https://huggingface.co) account with access token

---

## 🎯 Quick Start (Docker)

The fastest way to get started:

```bash
# Clone repository
git clone --recursive https://github.com/yourusername/provenance-guardian.git
cd provenance-guardian

# Configure environment
cp .env.example backend/.env
# Edit backend/.env and add:
# - HF_TOKEN=your_huggingface_token
# - FINGERPRINT_ENCRYPTION_KEY=generate_with_openssl

# Start with Docker
docker-compose up --build
```

Visit `http://localhost:5173` for the chat UI!

---

## 🔧 Manual Setup (Development)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install DeepSpeed from source
DS_BUILD_OPS=1 pip install deepspeed

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run setup script
chmod +x scripts/setup_guardian.sh
./scripts/setup_guardian.sh
```

### 2. Fingerprint the Guardian Model

This creates the agent's own fingerprinted model:

```bash
# This takes 1-3 hours on a single GPU
python scripts/fingerprint_model.py
```

**What this does:**
1. Generates 4,096 unique fingerprints
2. Fine-tunes Llama-3.1-8B with fingerprints
3. Encrypts and stores fingerprints securely
4. Sets up the guardian model for use

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local if needed (default should work)

# Start development server
npm run dev
```

### 4. Start the Application

**Terminal 1 (Backend):**
```bash
cd backend
source env/bin/activate
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173`

---

## ⚙️ Configuration

### Backend Configuration (.env)

```bash
# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
ENABLE_GPU=true

# Model Configuration
BASE_MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
MODEL_CACHE_DIR=./data/models

# Security (IMPORTANT!)
FINGERPRINT_ENCRYPTION_KEY=your-secret-key-here
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Hugging Face
HF_TOKEN=your_huggingface_token_here

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend Configuration (.env.local)

```bash
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing
1. Open `http://localhost:5173`
2. Try: "Verify yourself" (should show ✅ verified)
3. Try: "Generate fingerprints for me"
4. Try: "Audit this model: meta-llama/Llama-2-7b-hf" (will download model)

---

## 🐛 Troubleshooting

### "DeepSpeed not found"
```bash
# Reinstall DeepSpeed with ops
DS_BUILD_OPS=1 pip install deepspeed --no-cache-dir
```

### "CUDA out of memory"
- Enable quantization in `.env`: `ENABLE_MODEL_QUANTIZATION=true`
- Or use CPU mode: `ENABLE_GPU=false`

### "Model not found"
- Ensure HF_TOKEN is set in `.env`
- Check model cache: `ls backend/data/models/`

### "Fingerprints not loaded"
- Run `python scripts/fingerprint_model.py` first
- Check encrypted file: `ls backend/data/fingerprints/`

### Frontend can't connect to backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `backend/.env`

---

## 📊 Performance Tuning

### GPU Memory Optimization
```python
# In backend/agent/config.py, adjust:
enable_model_quantization = True  # Enables 8-bit quantization
```

### Audit Speed
```python
# Reduce sample sizes for faster audits:
quick_audit_sample_size = 25  # Default: 50
default_audit_sample_size = 50  # Default: 100
```

### Model Caching
```python
# Increase cache size:
model_cache_size_gb = 100  # Default: 50
```

---

## 🚀 Next Steps

1. **Test the agent**: Try all commands in the chat UI
2. **Deploy to Sentient**: See [DEPLOYMENT.md](DEPLOYMENT.md)
3. **Customize**: Modify agent responses in `backend/agent/provenance_guardian.py`
4. **Monitor**: Check logs in `backend/logs/guardian.log`

---

For more help, see:
- [API Documentation](API.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Troubleshooting](TROUBLESHOOTING.md)
