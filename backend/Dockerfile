FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install DeepSpeed from source (for OML)
RUN DS_BUILD_OPS=1 pip3 install deepspeed --no-cache-dir

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/models data/fingerprints data/audit_reports logs

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]