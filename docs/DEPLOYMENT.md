# 🚀 Deployment Guide

## Deploying to Sentient Chat

### Prerequisites
1. Approved Sentient Builder Program access
2. Fingerprinted guardian model ready
3. Agent tested locally

### Steps

#### 1. Prepare for Deployment

```bash
cd backend

# Ensure all tests pass
pytest tests/ -v

# Verify agent works locally
python -c "from agent.provenance_guardian import ProvenanceGuardian; print('✅ Agent OK')"
```

#### 2. Package Agent

```bash
# Create deployment package
tar -czf provenance-guardian.tar.gz \
  agent/ \
  fingerprints/ \
  models/ \
  utils/ \
  requirements.txt \
  data/fingerprints/*.enc
```

#### 3. Deploy via Sentient API

```python
# backend/scripts/deploy_to_sentient.py
import requests
from pathlib import Path
from agent.config import settings

SENTIENT_API_URL = "https://api.sentient.ai/v1"

def deploy_agent():
    # Authenticate
    headers = {
        "Authorization": f"Bearer {settings.sentient_api_key}",
        "Content-Type": "application/json"
    }
    
    # Register agent
    response = requests.post(
        f"{SENTIENT_API_URL}/agents/register",
        headers=headers,
        json={
            "name": settings.sentient_agent_name,
            "description": settings.sentient_agent_description,
            "version": "1.0.0",
            "capabilities": [
                "model_audit",
                "fingerprint_generation",
                "self_verification"
            ]
        }
    )
    
    agent_id = response.json()["agent_id"]
    print(f"✅ Agent registered: {agent_id}")
    
    # Upload code
    with open("provenance-guardian.tar.gz", "rb") as f:
        files = {"package": f}
        response = requests.post(
            f"{SENTIENT_API_URL}/agents/{agent_id}/upload",
            headers={"Authorization": headers["Authorization"]},
            files=files
        )
    
    print("✅ Agent deployed to Sentient Chat!")
    print(f"Users can summon with: @{settings.sentient_agent_name}")

if __name__ == "__main__":
    deploy_agent()
```

Run deployment:
```bash
python scripts/deploy_to_sentient.py
```

#### 4. Test on Sentient Chat

1. Open Sentient Chat
2. Try: `@ProvenanceGuardian verify yourself`
3. Try: `@ProvenanceGuardian audit meta-llama/Llama-2-7b-hf`

---

## Production Deployment (Self-Hosted)

### Using Docker

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Run in production mode
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f backend
```

### Using Kubernetes

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: provenance-guardian
spec:
  replicas: 2
  selector:
    matchLabels:
      app: provenance-guardian
  template:
    metadata:
      labels:
        app: provenance-guardian
    spec:
      containers:
      - name: backend
        image: provenance-guardian:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "8Gi"
            nvidia.com/gpu: 1
          limits:
            memory: "16Gi"
            nvidia.com/gpu: 1
```

Apply:
```bash
kubectl apply -f k8s/deployment.yaml
```

---

## Monitoring & Maintenance

### Health Checks
```bash
# Backend health
curl http://your-domain:8000/health

# Agent status
curl http://your-domain:8000/api/v1/health
```

### Logs
```bash
# Docker
docker-compose logs -f backend

# Direct
tail -f backend/logs/guardian.log
```

### Updates
```bash
# Pull latest code
git pull origin main

# Rebuild
docker-compose build

# Deploy
docker-compose up -d
```

---

## Security Considerations

1. **Encryption Keys**: Rotate `FINGERPRINT_ENCRYPTION_KEY` periodically
2. **API Access**: Use rate limiting and authentication
3. **Model Storage**: Encrypt fingerprinted models at rest
4. **Audit Logs**: Monitor audit requests for abuse
5. **CORS**: Restrict origins in production