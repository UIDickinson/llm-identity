# 🛡️ Provenance Guardian

**A Self-Verifying AI Model Auditor powered by Sentient OML Fingerprinting**

Provenance Guardian is an autonomous agent that audits AI models for ownership verification, helps users fingerprint their own models, and provides real-time provenance checking through an intuitive chat interface.

## 🌟 Features

- **🔍 Model Auditing**: Verify model ownership using OML 1.0 fingerprinting
- **🔐 Self-Verification**: Agent proves its own authenticity on demand
- **🎨 User Fingerprinting**: Guide users through securing their models
- **⚡ Real-Time Streaming**: Live updates via Server-Sent Events
- **🎯 Multi-Mode Audits**: Quick scan (2min) or Deep audit (10min)
- **🌐 Dual Deployment**: Local testing + Sentient Chat integration

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- CUDA-capable GPU (recommended) or CPU with 16GB+ RAM
- Hugging Face account (for model downloads)

### One-Command Setup
```bash
git clone --recursive https://github.com/yourusername/provenance-guardian.git
cd provenance-guardian
cp .env.example backend/.env
# Edit backend/.env with your HF_TOKEN and FINGERPRINT_ENCRYPTION_KEY
docker-compose up --build
```

Visit `http://localhost:5173` for the chat UI.

## 📖 Documentation

- [Setup Guide](docs/SETUP.md) - Detailed installation instructions
- [API Documentation](docs/API.md) - REST API reference
- [Architecture](docs/ARCHITECTURE.md) - System design overview
- [Deployment to Sentient](docs/DEPLOYMENT.md) - Production deployment guide

## 🎯 Usage Examples

### Chat Commands
```
"Audit this model: meta-llama/Llama-2-7b-hf"
"Verify yourself"
"How do I fingerprint my model?"
"Quick scan: my-model.safetensors"
"Deep audit mode: suspicious-model"
```

### API Usage
```bash
curl -X POST http://localhost:8000/api/v1/audit \
  -H "Content-Type: application/json" \
  -d '{"model_path": "meta-llama/Llama-2-7b-hf", "mode": "quick"}'
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Generate test models
python scripts/generate_test_models.py

# Frontend tests
cd frontend
npm test
```

## 📦 Project Structure

See [Project Structure](docs/ARCHITECTURE.md#structure) for detailed layout.

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- [Sentient Agent Framework](https://github.com/sentient-agi/Sentient-Agent-Framework)
- [OML 1.0 Fingerprinting](https://github.com/sentient-agi/OML-1.0-Fingerprinting)
- [Hugging Face Transformers](https://huggingface.co/transformers)

---

**⚠️ Security Notice**: This tool is for legitimate ownership verification only. Always respect model licenses and usage terms.