#!/bin/bash

echo "🛡️ Provenance Guardian Setup Script"
echo "===================================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv env
source env/bin/activate

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install DeepSpeed
echo "🚀 Installing DeepSpeed from source..."
DS_BUILD_OPS=1 pip install deepspeed

# Clone OML repository
if [ ! -d "../oml-fingerprinting" ]; then
    echo "📥 Cloning OML Fingerprinting repository..."
    cd ..
    git clone https://github.com/sentient-agi/OML-1.0-Fingerprinting oml-fingerprinting
    cd backend
fi

# Create directories
echo "📁 Creating data directories..."
mkdir -p data/models data/fingerprints data/audit_reports logs

# Generate encryption key
if [ ! -f ".env" ]; then
    echo "🔐 Generating encryption key..."
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    
    cp .env.example .env
    sed -i "s/your-secret-key-here-generate-with-openssl/$ENCRYPTION_KEY/" .env
    
    echo "✅ .env file created with encryption key"
    echo "⚠️  Please add your HF_TOKEN to .env"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your HuggingFace token to .env (HF_TOKEN=...)"
echo "2. Run: python scripts/fingerprint_model.py"
echo "3. Run: uvicorn api.server:app --reload"