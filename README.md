# 🛡️ Provenance Guardian

**AI Model Authenticity Auditor which utilises Sentient OML Fingerprinting and its Agent Framework**

A production-ready backend agent that audits AI models for ownership verification, helps users fingerprint their models, and provides real-time provenance checking.

---

## Features

- **Model Auditing** - Verify model ownership using OML 1.0 fingerprinting
- **Self-Verification** - Agent proves its own authenticity
- **Fingerprint Generation** - Generate custom fingerprints for users (100 fingerprints in <1s)
- **Real-Time Streaming** - SSE event streaming for live updates
- **Multi-Mode Audits** - Quick (2min), Standard (5min), Deep (10min)
- **RESTful API** - FastAPI server with comprehensive endpoints
- **Secure Storage** - Encrypted fingerprint storage

---

## Quick Start

### Prerequisites

- Python 3.10+
- pip
- 4GB+ RAM (16GB+ recommended)
- CUDA-capable GPU (optional, for faster inference)

### Installation
```bash
# 1. Clone repository
git clone https://github.com/UIDickinson/provenance-guardian.git
cd provenance-guardian/backend

# 2. Create virtual environment
python3 -m venv env
source env/bin/activate
# On Windows
env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.basic .env
# Edit .env with your settings (HF_TOKEN, FINGERPRINT_ENCRYPTION_KEY)

# 5. Create data directories
mkdir -p data/{models,fingerprints,audit_reports} logs
```

### Configuration

Create `.env` file:
```bash
# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
ENABLE_GPU=false

# Model Configuration
BASE_MODEL_NAME=gpt2
MODEL_CACHE_DIR=./data/models
FINGERPRINT_DIR=./data/fingerprints

# Security (CHANGE THIS!)
FINGERPRINT_ENCRYPTION_KEY=generate-secure-key-here

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Optional
HF_TOKEN=your_huggingface_token
```

**Generate encryption key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## Testing

### Quick Test (No Model Required)
```bash
# Set Python path and run agent tests
PYTHONPATH=/workspaces/llm-identity/backend python scripts/test_agent_locally.py
```

**Expected output:**
```
🧪 Provenance Guardian Local Test Suite
============================================================
Testing: help
✅ Received events
Testing: verify yourself
✅ Received events
Testing: generate fingerprints for me
✅ Generated 100 fingerprints
============================================================
✅ Test suite complete!
```

### Comprehensive Tests
```bash
# Run all function tests
PYTHONPATH=/workspaces/llm-identity/backend python test_all_functions.py
```

**Expected:**
```
============================================================
Total: 12 | Passed: 12 | Failed: 0
============================================================
```

### Unit Tests
```bash
# Run pytest suite
pytest tests/ -v

# With coverage
pytest tests/ --cov=agent --cov=api --cov=models
```

---

## Running the Agent

### Option 1: Without Frontend (CLI Testing)

**Interactive Test:**
```bash
PYTHONPATH=/workspaces/llm-identity/backend python scripts/test_agent_locally.py
```

### Option 2: With API Server

**Start server:**
```bash
# With helper script
./run_backend.sh

# Or directly - I recommend you use this lol. I'm not sure I'd set the above script config
PYTHONPATH=/workspaces/llm-identity/backend uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

**Test endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# Generate fingerprints
curl -X POST http://localhost:8000/api/v1/fingerprints/generate \
  -H "Content-Type: application/json" \
  -d '{"num_fingerprints":10,"key_length":10,"response_length":10}' | jq

# Chat (SSE streaming)
curl -X POST http://localhost:8000/api/v1/assist \
  -H "Content-Type: application/json" \
  -d '{"message":"help"}' \
  --no-buffer
```

### Option 3: Using CLI Tool
```bash
# Show system info
python scripts/cli.py info

# Generate fingerprints
python scripts/cli.py generate-fingerprints --num 5 --key-length 16 --response-length 16 --output my_fingerprints.json # larger fingerprints takes more time but are safer due to its length

# Serve API
python scripts/cli.py serve --port 8000
```

---

## API Endpoints

### Base URL: `http://localhost:8000`

#### Health Checks
- `GET /health` - Server health
- `GET /api/v1/health` - API health

#### Chat Interface
- `POST /api/v1/assist` - Main chat endpoint (SSE streaming)
```json
  {
    "message": "help",
    "session_id": "optional"
  }
```

#### Fingerprints
- `POST /api/v1/fingerprints/generate` - Generate fingerprints
```json
  {
    "num_fingerprints": 100,
    "key_length": 32,
    "response_length": 32
  }
```

#### Model Audit
- `POST /api/v1/audit` - Direct audit endpoint
```json
  {
    "model_path": "meta-llama/Llama-2-7b-hf",
    "mode": "quick"
  }
```

---

## 🔧 Troubleshooting

### Issue: Module not found
```bash
# Always set PYTHONPATH
export PYTHONPATH=/path/to/backend:$PYTHONPATH

# Or use helper scripts
./run_backend.sh
```

### Issue: CUDA out of memory
```bash
# In .env
ENABLE_GPU=false
ENABLE_MODEL_QUANTIZATION=true
```

### Issue: Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn api.server:app --port 8001
```

### Issue: Fingerprints not found
This is normal if you haven't run model fingerprinting yet (1-3 hours process).
The agent will work without fingerprints for testing.

---

## Performance

- **Agent Response Time**: <1s for most commands
- **Fingerprint Generation**: 100 fingerprints in <1s
- **API Latency**: <100ms for REST endpoints
- **Memory Usage**: ~500MB (without models loaded)
- **CPU Usage**: Low (~5-10%)

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Please your recommendations and corrections are highly valuable.

# Contact: x.com/ui_anon