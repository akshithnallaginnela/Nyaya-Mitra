#!/bin/bash
# ============================================
# Nyaya Mitra — Ollama Setup on EC2
# ============================================
# Run this on your EC2 instance to set up the AI layer
# Works on Amazon Linux 2023 or Ubuntu 22.04
#
# For GPU instances (g4dn.xlarge):
#   - NVIDIA drivers are pre-installed on AWS GPU AMIs
#   - Ollama will auto-detect GPU
#
# For CPU instances (t3.medium+):
#   - Use smaller model: llama3.2:3b
# ============================================

set -euo pipefail

echo "============================================"
echo "  Nyaya Mitra — Ollama AI Setup"
echo "============================================"
echo ""

# ─── Install Ollama ───
echo "[1/4] Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# ─── Configure as systemd service ───
echo "[2/4] Configuring Ollama service..."

sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama AI Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ollama
Group=ollama
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_MODELS=/opt/ollama/models"
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

# Create ollama user and directories
sudo useradd -r -s /bin/false -d /opt/ollama ollama 2>/dev/null || true
sudo mkdir -p /opt/ollama/models
sudo chown -R ollama:ollama /opt/ollama

# Start service
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

echo "  ✅ Ollama service started"
echo ""

# ─── Wait for Ollama to be ready ───
echo "[3/4] Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "  ✅ Ollama is ready"
        break
    fi
    sleep 2
done

# ─── Pull models ───
echo "[4/4] Pulling AI models..."

# Check if GPU is available
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "  GPU detected! Pulling larger model..."
    ollama pull mistral:7b
    echo "  ✅ mistral:7b pulled"
else
    echo "  CPU-only mode. Pulling smaller model..."
    ollama pull llama3.2:3b
    echo "  ✅ llama3.2:3b pulled"
fi

echo ""
echo "============================================"
echo "  ✅ Ollama AI Setup Complete!"
echo "============================================"
echo ""
echo "  API: http://localhost:11434"
echo "  Test: curl http://localhost:11434/api/tags"
echo ""
echo "  Service commands:"
echo "    sudo systemctl status ollama"
echo "    sudo systemctl restart ollama"
echo "    journalctl -u ollama -f"
echo "============================================"
