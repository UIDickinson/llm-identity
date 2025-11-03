#!/bin/bash
set -e

echo "🛡️ Provenance Guardian Backend"

# Check if fingerprinted model exists
if [ ! -d "data/models/guardian_model" ]; then
    echo "⚠️  Guardian model not found"
    echo "Run: python scripts/fingerprint_model.py"
    echo "Continuing anyway (will use base model)..."
fi

# Check if fingerprints exist
if [ ! -f "data/fingerprints/guardian_master_fingerprints.enc" ]; then
    echo "⚠️  Master fingerprints not found"
    echo "Self-verification will not work"
fi

# Start server
echo "🚀 Starting server..."
exec "$@"