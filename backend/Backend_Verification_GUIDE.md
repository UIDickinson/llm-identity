# 🧪 Backend Testing & Verification Guide

## Complete Backend Setup & Testing Workflow

This guide walks you through setting up and verifying the Provenance Guardian backend is working correctly **before** integrating the frontend.

---

## 📋 Pre-Testing Checklist

### 1. Verify System Requirements

```bash
cd backend
python scripts/check_setup.py
```

This script checks:
- ✅ Python 3.10+
- ✅ Required packages installed
- ✅ DeepSpeed available
- ✅ CUDA (if GPU available)
- ✅ `.env` file configured
- ✅ Required directories exist
- ✅ OML repository cloned

**Expected Output:**
```
✅ All checks passed! You're ready to go.
```

---

## 🔧 Step-by-Step Backend Setup

### Step 1: Install Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Install DeepSpeed (required for fingerprinting)
DS_BUILD_OPS=1 pip install deepspeed
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Generate encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Edit .env with:
nano .env  # or your preferred editor
```

**Required settings in `.env`:**
```bash
HF_TOKEN=hf_your_huggingface_token_here
FINGERPRINT_ENCRYPTION_KEY=<paste_generated_key_above>
```

### Step 3: Clone OML Repository

```bash
cd ..  # Go to project root
git clone https://github.com/sentient-agi/OML-1.0-Fingerprinting oml-fingerprinting
cd backend
```

---

## 🔐 Step 4: Fingerprint the Guardian Model

**⚠️ CRITICAL STEP**: This creates the agent's own fingerprinted model.

```bash
python scripts/fingerprint_model.py
```

**What happens:**
1. Downloads Llama-3.1-8B-Instruct (~7GB)
2. Generates 4,096 fingerprints
3. Fine-tunes model (1-3 hours on GPU, longer on CPU)
4. Encrypts and stores fingerprints
5. Saves fingerprinted model

**Expected Output:**
```
🔐 Starting Guardian Model Fingerprinting
🔑 Generating fingerprints...
✅ Fingerprints generated
🛠️ Fingerprinting model (this may take 1-3 hours)...
[Training logs...]
✅ Model fingerprinting complete
📦 Fingerprinted model at: ...
🔐 Encrypting and storing fingerprints...
✅ Guardian setup complete!
```

**Verify files were created:**
```bash
ls -lh data/models/guardian_model/
ls -lh data/fingerprints/guardian_master_fingerprints.enc
```

---

## 🧪 Testing the Backend

### Test 1: Quick Agent Test

```bash
bash scripts/quick_test.sh
```

**Tests:**
- Agent initialization
- Help command
- Self-verification command

**Expected Output:**
```
🧪 Quick Agent Test
==================

1. Testing agent initialization...
   ✅ Agent initialized

2. Testing help command...
   ✅ Help command works

3. Testing self-verification...
   ✅ Self-verification command works

✅ All quick tests passed!
```

### Test 2: Comprehensive Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_agent.py -v
pytest tests/test_fingerprint_service.py -v
pytest tests/test_storage.py -v
```

**Expected Output:**
```
tests/test_agent.py::test_agent_initialization PASSED
tests/test_agent.py::test_parse_intent PASSED
tests/test_fingerprint_service.py::test_generate_fingerprints_basic PASSED
tests/test_storage.py::test_save_and_load_encrypted PASSED
...
==================== X passed in Y.YYs ====================
```

### Test 3: Integration Tests

```bash
pytest tests/ -v -m integration
```

**These test:**
- Full agent command flow
- API endpoints
- SSE streaming

### Test 4: Local Agent Testing (Interactive)

```bash
python scripts/test_agent_locally.py
```

**Tests each command:**
- `help`
- `verify yourself`
- `how do I fingerprint my model?`
- `generate fingerprints for me`

**Expected Output:**
```
Testing: help
============================================================
Events received:
[Event 1]
Type: TEXT_BLOCK
Content: 🛡️ **Provenance Guardian Commands**...

Testing: verify yourself
============================================================
[Event 1]
Type: JSON
Event Type: SELF_VERIFICATION
[Event 2]
Type: TEXT_BLOCK
Content: ✅ **Self-Verification PASSED**...
```

---

## 🚀 Test 5: Start the API Server

### Option A: Development Mode

```bash
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

### Option B: Using Makefile

```bash
make dev
```

### Option C: Using CLI

```bash
python scripts/cli.py serve --reload
```

**Expected Output:**
```
🚀 Starting Provenance Guardian API...
✅ API ready
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🔍 Test 6: API Endpoint Testing

### Test Health Endpoints

```bash
# Root endpoint
curl http://localhost:8000/
# Expected: {"name":"Provenance Guardian API","version":"1.0.0",...}

# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# API health
curl http://localhost:8000/api/v1/health
# Expected: {"status":"healthy","service":"provenance-guardian"}
```

### Test Chat Endpoint (SSE)

```bash
# This will stream events (Ctrl+C to stop)
curl -X POST http://localhost:8000/api/v1/assist \
  -H "Content-Type: application/json" \
  -d '{"message":"help"}' \
  --no-buffer

# Expected: Stream of SSE events
# data: {"type":"text_block","event_type":"HELP","content":"🛡️ **Provenance Guardian Commands**..."}
# data: {"type":"done"}
```

### Test Direct Audit Endpoint

```bash
# Note: This will fail if you don't have the model or fingerprints
# But it tests the endpoint works
curl -X POST http://localhost:8000/api/v1/audit \
  -H "Content-Type: application/json" \
  -d '{
    "model_path": "test-model",
    "mode": "quick"
  }'

# Expected: JSON response with audit results or error
```

### Test Fingerprint Generation

```bash
curl -X POST http://localhost:8000/api/v1/fingerprints/generate \
  -H "Content-Type: application/json" \
  -d '{
    "num_fingerprints": 5,
    "key_length": 10,
    "response_length": 10
  }' | jq

# Expected: JSON with queries, responses, metadata
```

---

## 🎯 Test 7: CLI Tool Testing

### Test CLI Commands

```bash
# Show system info
python scripts/cli.py info

# Generate fingerprints
python scripts/cli.py generate-fingerprints --num 10 --output test_fingerprints.json

# Encrypt fingerprints
python scripts/cli.py encrypt-fingerprints test_fingerprints.json test_fingerprints.enc
```

---

## 📊 Test 8: Performance Benchmarking

```bash
python scripts/benchmark.py
```

**Measures:**
- Help command latency
- Self-verification speed
- Fingerprint generation time

**Expected Output:**
```
⏱️  Provenance Guardian Performance Benchmark
============================================================
Benchmarking: help
Iterations: 3
  Run 1: 0.234s
  Run 2: 0.189s
  Run 3: 0.201s

Results:
  Average: 0.208s
  Min: 0.189s
  Max: 0.234s
...
```

---

## ✅ Verification Checklist

Mark each as complete:

### Core Functionality
- [ ] Agent initializes without errors
- [ ] Help command works
- [ ] Self-verification passes (if model fingerprinted)
- [ ] Fingerprint generation works
- [ ] Setup guide returns correctly

### API Endpoints
- [ ] Root endpoint responds
- [ ] Health checks pass
- [ ] SSE streaming works
- [ ] JSON responses are valid
- [ ] Error handling works

### Storage & Security
- [ ] Fingerprints encrypt/decrypt correctly
- [ ] No plaintext fingerprints in encrypted files
- [ ] Encryption key is secure

### Performance
- [ ] Commands respond in < 1 second
- [ ] No memory leaks during tests
- [ ] GPU is utilized (if available)

---

## 🐛 Troubleshooting

### Agent Fails to Initialize

**Error:** `ModuleNotFoundError: No module named 'sentient_agent_framework'`

**Fix:**
```bash
pip install sentient-agent-framework
```

### Fingerprints Not Found

**Error:** `⚠️ Master fingerprints not found`

**Fix:**
```bash
# Re-run fingerprinting
python scripts/fingerprint_model.py

# Or use test fingerprints
python scripts/cli.py generate-fingerprints --num 100 --output data/fingerprints/test.json
python scripts/cli.py encrypt-fingerprints data/fingerprints/test.json data/fingerprints/guardian_master_fingerprints.enc
```

### CUDA Out of Memory

**Error:** `RuntimeError: CUDA out of memory`

**Fix:**
```bash
# In .env
ENABLE_MODEL_QUANTIZATION=true

# Or use CPU mode
ENABLE_GPU=false
```

### API Port Already in Use

**Error:** `Address already in use`

**Fix:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn api.server:app --port 8001
```

---

## 🎉 Success Criteria

Your backend is **ready for frontend integration** when:

✅ All unit tests pass  
✅ Integration tests pass  
✅ API server starts without errors  
✅ All health endpoints respond  
✅ SSE streaming works  
✅ Self-verification passes (with fingerprinted model)  
✅ No errors in logs  

---

## 📝 Next Steps

Once all tests pass:

1. **Keep the backend running:**
   ```bash
   uvicorn api.server:app --reload
   ```

2. **Proceed to frontend setup** (in separate terminal)

3. **Test full stack integration**

---

## 📚 Additional Resources

- **API Documentation**: See OpenAPI docs at `http://localhost:8000/docs`
- **Logs**: Check `backend/logs/guardian.log`
- **Debug Mode**: Set `LOG_LEVEL=DEBUG` in `.env`