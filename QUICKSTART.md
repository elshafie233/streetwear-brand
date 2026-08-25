# QUICK REFERENCE — GitHub Codespaces

## One-Command Start
```bash
source venv/bin/activate && uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

## Common Commands

### Activate Environment
```bash
source venv/bin/activate
```

### Test Components
```bash
python fit_predictor.py      # FREE — Size prediction
python trend_scraper.py      # FREE — Trend monitoring
python inspiration_analyzer.py  # FREE — Image analysis (first run downloads ~500MB)
python rag_stylist.py        # $0.50/mo — AI stylist (needs API key)
```

### Start API
```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Install New Packages
```bash
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt
```

### Update .env
```bash
nano .env
# Edit, then: Ctrl+O, Enter, Ctrl+X
```

## Troubleshooting

**"Module not found"**
→ Run: `source venv/bin/activate`

**"Permission denied"**
→ Run: `chmod +x setup.sh`

**"Port already in use"**
→ Run: `uvicorn api_server:app --reload --host 0.0.0.0 --port 8001`

**"OpenAI API key invalid"**
→ Check `.env` file exists and has correct key
→ Run: `cat .env` to verify

**Codespaces sleeping?**
→ Just open it again. Work is saved.

## Port Forwarding
Codespaces auto-forwards these ports:
- **8000** — FastAPI backend
- **3000** — Next.js frontend (if you add one)

Find your public URL in the **Ports** tab (globe icon).
