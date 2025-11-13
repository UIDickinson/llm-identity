# 🛡️ Provenance Guardian - Complete Quick Start Guide

## features
- ✅ Audits AI models for ownership fingerprints using Sentient OML 1.0
- ✅ Verifies its own authenticity on demand
- ✅ Helps users fingerprint their models
- ✅ Features a sleek React chat UI for local testing
- ✅ Deployable to Sentient Chat for public use

---

## 📋 Prerequisites Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Git installed
- [ ] NVIDIA GPU with CUDA 12.1+ (or 16GB+ RAM for CPU mode)
- [ ] Hugging Face account with token ([get one here](https://huggingface.co/settings/tokens))
- [ ] 50GB+ free disk space
- [ ] Docker & Docker Compose (optional, for easy deployment)

---

## 🚀 Option 1: Quick Start with Docker (Recommended)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/UIDickinson/llm-identity.git
cd llm-identity

# Initialize OML submodule
git submodule init
git submodule update

# If you can't initialize oml- clone the oml repo in the llm-identity root dir
git clone https://github.com/sentient-agi/OML-1.0-Fingerprinting.git

"""
you can may rename the dir from OML-1.0-Fingerprinting to oml-fingerprinting for smooth run
"""
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example backend/.env

# Generate encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Edit backend/.env and set:
nano backend/.env
```

**Required settings in `.env`:**
```bash
HF_TOKEN=hf_your_token_here
FINGERPRINT_ENCRYPTION_KEY=your_generated_key_from_above
```

### Step 3: Setup and Fingerprint the Guardian Model

**⚠️ IMPORTANT**: This step takes 1-3 hours. Run it first!

```bash
cd backend
python3 -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
DS_BUILD_OPS=1 pip install deepspeed

# Test before fingerprinting
chmod +x test_all_functions.py

PYTHONPATH=/workspaces/llm-identity/backend python test_all_functions.py # test all functions

#---------------------
# test api server

# Terminal 1: Start server
./run_backend.sh

# Or with explicit PYTHONPATH
PYTHONPATH=/workspaces/llm-identity/backend uvicorn api.server:app --reload --host 0.0.0.0 --port 8000

# Open another terminal and run the below to test api endpoints and performance
chmod +x test_api_endpoints.sh

./test_api_endpoints.sh

chmod +x test_performance.py

PYTHONPATH=/workspaces/llm-identity/backend python test_performance.py

# Run fingerprinting (go get coffee ☕)
python scripts/fingerprint_model.py
```

**What this does:**
1. Generates 4,096 secret fingerprints
2. Downloads Llama-3.1-8B-Instruct (7GB)
3. Fine-tunes it with fingerprints
4. Encrypts and stores fingerprints
5. Saves the fingerprinted model

### Step 4: Launch with Docker

```bash
# Back to root directory
cd ..

# Start everything
docker-compose up --build
```

**Wait for these messages:**
```
✅ Backend: Provenance Guardian initialized successfully
✅ Frontend: Local: http://localhost:5173
```

### Step 5: Test It!

Open `http://localhost:5173` and try:

1. **"Verify yourself"** → Should show ✅ with fingerprint proofs
2. **"Generate fingerprints for me"** → Downloads custom fingerprint JSON
3. **"Audit this model: meta-llama/Llama-2-7b-hf"** → Runs audit (2-3 min)

---

## 🔧 Option 2: Manual Setup (Full Control)

### Step 1: Backend Setup

```bash
cd backend

# Virtual environment
python3 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
DS_BUILD_OPS=1 pip install deepspeed

# Setup environment
cp .env.example .env
# Edit .env with HF_TOKEN and FINGERPRINT_ENCRYPTION_KEY

# Create directories
mkdir -p data/models data/fingerprints data/audit_reports logs

# Clone OML
cd ..
git clone https://github.com/sentient-agi/OML-1.0-Fingerprinting oml-fingerprinting
cd backend
```

### Step 2: Fingerprint Model

```bash
python scripts/fingerprint_model.py
```

### Step 3: Frontend Setup

```bash
# New terminal
cd frontend

npm install

# Configure
cp .env.example .env.local
# Default should work, or edit VITE_API_URL if needed

npm run dev
```

### Step 4: Start Backend

```bash
# Terminal 1
cd backend
source env/bin/activate
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:5173`

---

## 🧪 Verify Everything Works

### Test Checklist

Run these commands in the chat UI:

1. **Self-Verification**
   ```
   Verify yourself
   ```
   Expected: ✅ Verification PASSED with 3 fingerprint proofs

2. **Generate Fingerprints**
   ```
   Generate fingerprints for me
   ```
   Expected: JSON download with 100 fingerprints

3. **Audit Model (Quick)**
   ```
   Quick scan: meta-llama/Llama-2-7b-hf
   ```
   Expected: Audit completes in 1-2 minutes

4. **Get Help**
   ```
   help
   ```
   Expected: Command list displayed

### Backend Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy", "service": "provenance-guardian"}
```

---

## 📁 Project Structure Overview

```
provenance-guardian/
├── backend/              # Python FastAPI + Sentient Agent
│   ├── agent/           # Core agent logic
│   ├── fingerprints/    # OML integration
│   ├── models/          # Model loading
│   ├── api/             # FastAPI server
│   └── scripts/         # Setup & deployment scripts
├── frontend/            # React + Vite chat UI
│   └── src/
│       ├── components/  # Chat interface
│       ├── services/    # API & SSE clients
│       └── hooks/       # React hooks
├── oml-fingerprinting/  # Sentient OML (submodule)
└── docs/               # Documentation
```

---

## 🎨 UI Features

### Chat Interface
- Real-time streaming responses (SSE)
- Syntax-highlighted code blocks
- Interactive audit reports with charts
- Downloadable fingerprint JSON
- Responsive design with Tailwind CSS

### Agent Capabilities
- Model auditing (quick/standard/deep modes)
- Self-verification with cryptographic proofs
- Fingerprint generation for users
- Step-by-step setup guidance

---

## ⚙️ Configuration Tips

### For CPU-Only Systems

Edit `backend/.env`:
```bash
ENABLE_GPU=false
ENABLE_MODEL_QUANTIZATION=true
```

### For Faster Audits (Lower Accuracy)

Edit `backend/agent/config.py`:
```python
quick_audit_sample_size = 25      # Default: 50
default_audit_sample_size = 50     # Default: 100
```

### For Custom Base Model

Edit `backend/.env`:
```bash
BASE_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
```

Then re-run `python scripts/fingerprint_model.py`

---

## 🐛 Common Issues & Fixes

### Issue: "DeepSpeed not found"
```bash
sudo apt update
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
sudo apt install -y build-essential ninja-build python3-dev
pip install deepspeed
DS_BUILD_OPS=1 pip install deepspeed --no-cache-dir

# verify installations
import torch
import deepspeed
print(torch.__version__, deepspeed.__version__)
```

### Issue: "CUDA out of memory"
```bash
# In backend/.env
ENABLE_MODEL_QUANTIZATION=true
```

### Issue: "Frontend can't connect"
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS in backend/.env
CORS_ORIGINS=http://localhost:5173
```

### Issue: "Fingerprints not loaded"
```bash
# Re-run fingerprinting
cd backend
python scripts/fingerprint_model.py

# Verify file exists
ls data/fingerprints/guardian_master_fingerprints.enc
```

---

## 🚀 Next Steps

### 1. Test Thoroughly
- Try all chat commands
- Test with different models
- Check audit accuracy

### 2. Customize
- Modify agent responses in `backend/agent/provenance_guardian.py`
- Adjust UI styling in `frontend/src/components/`
- Add new features (e.g., batch audits, report exports)

### 3. Deploy to Sentient
See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Sentient Chat integration
- Production deployment (Docker/K8s)
- Monitoring & maintenance

### 4. Share Your Work
- Record a demo video
- Write a blog post
- Submit to Sentient Builder Program
- Apply for featured agent status

---

## 📚 Additional Resources

- **API Documentation**: [docs/API.md](docs/API.md)
- **Architecture Details**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Sentient Docs**: https://docs.sentient.ai
- **OML Paper**: https://eprint.iacr.org/2024/1573

---

## 🤝 Need Help?

- **Discord**: [Join Sentient Community]
- **GitHub Issues**: [Report bugs]
- **Email**: support@yourproject.com

---

## ✨ Pro Tips

1. **Test locally first**: Verify everything works before deploying
2. **Keep fingerprints secret**: Treat them like private keys
3. **Monitor performance**: Check logs for errors/slowdowns
4. **Start small**: Use quick audits for testing, deep audits for production
5. **Backup data**: Regularly backup `backend/data/fingerprints/`

---

**🎉 Congratulations!** You now have a fully functional AI model provenance auditor. 