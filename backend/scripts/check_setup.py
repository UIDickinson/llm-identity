import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (need 3.10+)")
        return False


def check_imports():
    """Check if required packages are installed"""
    packages = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("fastapi", "FastAPI"),
        ("sentient_agent_framework", "Sentient Agent Framework"),
        ("cryptography", "Cryptography"),
    ]
    
    all_ok = True
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} (run: pip install {package})")
            all_ok = False
    
    return all_ok


def check_deepspeed():
    """Check DeepSpeed installation"""
    try:
        import deepspeed
        print(f"✅ DeepSpeed {deepspeed.__version__}")
        return True
    except ImportError:
        print("❌ DeepSpeed (run: DS_BUILD_OPS=1 pip install deepspeed)")
        return False


def check_cuda():
    """Check CUDA availability"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA {torch.version.cuda}")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("⚠️  CUDA not available (CPU mode will be used)")
            return True
    except:
        print("⚠️  Could not check CUDA")
        return True


def check_env_file():
    """Check if .env exists and has required keys"""
    env_file = Path(__file__).parent.parent / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        return False
    
    print("✅ .env file exists")
    
    # Check for required keys
    with open(env_file) as f:
        content = f.read()
    
    required = [
        "HF_TOKEN",
        "FINGERPRINT_ENCRYPTION_KEY"
    ]
    
    missing = []
    for key in required:
        if key not in content or f"{key}=your-" in content:
            missing.append(key)
    
    if missing:
        print(f"⚠️  Missing or not configured: {', '.join(missing)}")
        return False
    
    return True


def check_directories():
    """Check if required directories exist"""
    base = Path(__file__).parent.parent
    dirs = [
        base / "data" / "models",
        base / "data" / "fingerprints",
        base / "data" / "audit_reports",
        base / "logs"
    ]
    
    all_ok = True
    for dir_path in dirs:
        if dir_path.exists():
            print(f"✅ {dir_path.relative_to(base)}")
        else:
            print(f"❌ {dir_path.relative_to(base)} (creating...)")
            dir_path.mkdir(parents=True, exist_ok=True)
            all_ok = False
    
    return all_ok


def check_oml_repo():
    """Check if OML repository is available"""
    oml_path = Path(__file__).parent.parent.parent / "oml-fingerprinting"
    
    if oml_path.exists():
        print(f"✅ OML repository at {oml_path}")
        return True
    else:
        print(f"⚠️  OML repository not found at {oml_path}")
        print("   Run: git clone https://github.com/sentient-agi/OML-1.0-Fingerprinting ../oml-fingerprinting")
        return False


def main():
    """Run all checks"""
    print("🔍 Provenance Guardian Setup Check\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_imports),
        ("DeepSpeed", check_deepspeed),
        ("CUDA", check_cuda),
        ("Environment File", check_env_file),
        ("Directories", check_directories),
        ("OML Repository", check_oml_repo),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        result = check_func()
        results.append(result)
    
    print("\n" + "="*60)
    
    if all(results):
        print("✅ All checks passed! You're ready to go.")
        print("\nNext steps:")
        print("1. Run: python scripts/fingerprint_model.py")
        print("2. Run: python scripts/test_agent_locally.py")
        print("3. Run: uvicorn api.server:app --reload")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()