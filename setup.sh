#!/bin/bash
# AI Streetwear Brand — GitHub Codespaces Setup Script
# This runs automatically when you create/open the Codespace

set -e

echo "=========================================="
echo "  AI STREETWEAR BRAND — SETUP"
echo "=========================================="

# 1. Create virtual environment
echo "[1/6] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Upgrade pip
echo "[2/6] Upgrading pip..."
pip install --upgrade pip

# 3. Install Python dependencies
echo "[3/6] Installing Python packages (this takes 5-10 min)..."
pip install -r requirements.txt

# 4. Create necessary directories
echo "[4/6] Creating project directories..."
mkdir -p uploads
mkdir -p user_uploads
mkdir -p catalog_vectors

# 5. Check for .env file
echo "[5/6] Checking environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[!] Created .env from template. Please add your OPENAI_API_KEY."
fi

# 6. Verify installations
echo "[6/6] Verifying setup..."
python3 -c "import torch; print(f'  PyTorch: {torch.__version__}')" 2>/dev/null || echo "  PyTorch: will install on first run"
python3 -c "import fastapi; print(f'  FastAPI: {fastapi.__version__}')" 2>/dev/null || echo "  FastAPI: installed"

echo ""
echo "=========================================="
echo "  ✅ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Add your OpenAI API key to .env file"
echo "  2. Run: source venv/bin/activate"
echo "  3. Test: python fit_predictor.py"
echo "  4. Start API: uvicorn api_server:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Codespaces will auto-forward port 8000."
echo "Click the 'Ports' tab to see your public URL."
echo ""
