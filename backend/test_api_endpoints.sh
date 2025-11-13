#!/bin/bash

echo "🌐 Testing API Endpoints"
echo "================================"

# Test 1: Root endpoint
echo -e "\n1️⃣ Testing root endpoint..."
curl -s http://localhost:8000/ | jq

# Test 2: Health check
echo -e "\n2️⃣ Testing health endpoint..."
curl -s http://localhost:8000/health | jq

# Test 3: API health
echo -e "\n3️⃣ Testing API health..."
curl -s http://localhost:8000/api/v1/health | jq

# Test 4: Generate fingerprints
echo -e "\n4️⃣ Testing fingerprint generation..."
curl -s -X POST http://localhost:8000/api/v1/fingerprints/generate \
  -H "Content-Type: application/json" \
  -d '{
    "num_fingerprints": 5,
    "key_length": 10,
    "response_length": 10
  }' | jq '.queries | length'

# Test 5: Chat endpoint (help)
echo -e "\n5️⃣ Testing chat endpoint (help)..."
curl -s -X POST http://localhost:8000/api/v1/assist \
  -H "Content-Type: application/json" \
  -d '{"message":"help"}' \
  --no-buffer | head -20

# Test 6: Chat endpoint (generate fingerprints)
echo -e "\n6️⃣ Testing chat endpoint (generate fingerprints)..."
curl -s -X POST http://localhost:8000/api/v1/assist \
  -H "Content-Type: application/json" \
  -d '{"message":"generate fingerprints for me"}' \
  --no-buffer | head -20

echo -e "\n\n✅ API endpoint tests complete!"