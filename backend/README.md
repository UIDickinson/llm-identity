# Provenance Guardian Backend

## Overview

Python backend for the Provenance Guardian AI model auditor, built with:
- **Sentient Agent Framework**: For agent logic and event streaming
- **OML 1.0 Fingerprinting**: For model authentication
- **FastAPI**: For REST API and SSE endpoints
- **PyTorch + Transformers**: For model loading and inference

## Quick Start

```bash
# Setup
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
DS_BUILD_OPS=1 pip install deepspeed

# Configure
cp .env.example .env
# Edit .env with your settings

# Initialize guardian model
python scripts/fingerprint_model.py

# Run server
uvicorn api.server:app --reload
```

## Project Structure

```
backend/
├── agent/              # Core agent logic
│   ├── provenance_guardian.py    # Main agent class
│   ├── audit_engine.py           # Audit logic
│   ├── fingerprint_service.py    # User fingerprinting
│   └── config.py                 # Configuration
├── api/                # FastAPI server
│   ├── server.py       # App initialization
│   ├── routes.py       # Endpoints
│   └── schemas.py      # Pydantic models
├── models/             # Model management
│   ├── loader.py       # Model loading
│   └── cache.py        # LRU cache
├── fingerprints/       # OML integration
│   ├── generator.py    # Fingerprint generation
│   ├── validator.py    # Verification
│   └── storage.py      # Secure storage
└── utils/              # Utilities
    ├── logger.py       # Logging
    ├── crypto.py       # Encryption
    └── validators.py   # Input validation
```

## API Endpoints

### Chat (SSE)
```
POST /api/v1/assist
Body: {"message": "audit model-name", "session_id": "optional"}
Returns: Server-Sent Events stream
```

### Direct Audit
```
POST /api/v1/audit
Body: {"model_path": "meta-llama/Llama-2-7b-hf", "mode": "quick"}
Returns: JSON audit result
```

### Generate Fingerprints
```
POST /api/v1/fingerprints/generate
Body: {"num_fingerprints": 100, "key_length": 32, "response_length": 32}
Returns: JSON fingerprint data
```

### Health Check
```
GET /health
GET /api/v1/health
Returns: {"status": "healthy"}
```

## Configuration

See `.env.example` for all available settings. Key configurations:

```bash
# Model
BASE_MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct

# Security
FINGERPRINT_ENCRYPTION_KEY=your-key-here

# Performance
ENABLE_GPU=true
ENABLE_MODEL_QUANTIZATION=true
MAX_CONCURRENT_AUDITS=2
```

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Style
```bash
black agent/ api/ models/ fingerprints/ utils/
flake8 agent/ api/ models/ fingerprints/ utils/
```

### Adding New Features

1. **New Agent Command**: Modify `agent/provenance_guardian.py`
2. **New API Endpoint**: Add to `api/routes.py`
3. **New Fingerprint Strategy**: Extend `fingerprints/generator.py`

## Troubleshooting

### DeepSpeed Issues
```bash
DS_BUILD_OPS=1 pip install deepspeed --no-cache-dir
```

### GPU Memory
- Enable quantization: `ENABLE_MODEL_QUANTIZATION=true`
- Reduce sample sizes in `agent/config.py`

### Model Loading Fails
- Check HF_TOKEN in `.env`
- Verify model exists on Hugging Face
- Check disk space (50GB+ recommended)

## License

MIT License - see LICENSE file