# 🤖 AI Streetwear Brand

**AI-native fashion brand built for Gen Z in Egypt.**

Upload photos of outfits you love → AI extracts your style → Predicts your perfect size → Curates outfits from our catalog.

Built with: Python, FastAPI, CLIP, OpenAI, FAISS

---

## 🚀 Quick Start (GitHub Codespaces)

### Step 1: Create a Codespace
1. Fork this repository (or create a new one and upload these files)
2. Click the green **"<> Code"** button
3. Select **"Codespaces"** tab
4. Click **"Create codespace on main"**
5. Wait 2-3 minutes for the container to build

### Step 2: Setup Runs Automatically
The `setup.sh` script runs automatically and:
- Creates a Python virtual environment
- Installs all dependencies
- Creates necessary folders
- Sets up `.env` file

### Step 3: Activate Environment
```bash
source venv/bin/activate
```

### Step 4: Add Your OpenAI API Key
```bash
# Edit the .env file
nano .env

# Add your key (get one at https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-key-here

# Save: Ctrl+O, Enter, Ctrl+X
```

### Step 5: Test Everything
```bash
# Test 1: Size predictor (no API key needed)
python fit_predictor.py

# Test 2: Trend scraper (no API key needed)
python trend_scraper.py

# Test 3: Image analyzer (downloads CLIP model, ~500MB)
python inspiration_analyzer.py

# Test 4: AI stylist (needs API key)
python rag_stylist.py
```

### Step 6: Start the API Server
```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

**Codespaces auto-forwards port 8000.**
- Click the **"Ports"** tab in VS Code
- You'll see port 8000 with a URL like `https://your-repo-8000.github.dev`
- Click the globe icon to open in browser
- Add `/docs` to the URL to see interactive API docs

---

## 📁 Project Structure

```
.
├── .devcontainer/
│   └── devcontainer.json      # Codespaces configuration
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── api_server.py              # FastAPI backend
├── fit_predictor.py           # Size prediction engine
├── inspiration_analyzer.py    # Photo style analysis (CLIP)
├── rag_stylist.py             # AI outfit recommender
├── trend_scraper.py           # Fashion trend monitoring
├── requirements.txt           # Python dependencies
├── setup.sh                   # Auto-setup script
└── README.md                  # This file
```

---

## 🔌 API Endpoints

| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/predict-size` | POST | Predict clothing size |
| `/api/analyze-inspiration` | POST | Analyze uploaded photos |
| `/api/get-outfit` | POST | Get AI-curated outfit |
| `/api/ask-stylist` | POST | Chat with AI stylist |
| `/api/trends` | GET | Fashion trend report |
| `/api/health` | GET | Service status check |
| `/docs` | GET | Interactive API documentation |

---

## 💰 Costs

| Component | Cost |
|-----------|------|
| GitHub Codespaces | **FREE** (60 hours/month) |
| Size Predictor | **FREE** |
| Trend Scraper | **FREE** |
| Image Analyzer (CLIP) | **FREE** |
| AI Stylist (OpenAI) | **~$0.50/month** |
| **Total** | **~$0.50/month** |

---

## 🛠️ Tech Stack

- **Python 3.11** — Backend logic
- **FastAPI** — API framework
- **CLIP (OpenAI)** — Free image style analysis
- **OpenAI GPT-4o-mini** — Outfit curation
- **FAISS** — Vector search for catalog
- **LangChain** — RAG pipeline
- **PyTorch** — Deep learning backend

---

## 📝 Example API Calls

### Predict Size
```bash
curl -X POST "https://your-url-8000.github.dev/api/predict-size" \
  -H "Content-Type: application/json" \
  -d '{
    "known_brand": "zara",
    "known_size": "M",
    "height_cm": 178,
    "weight_kg": 75,
    "body_type": "athletic",
    "fit_preference": "oversized"
  }'
```

### Get Outfit Recommendation
```bash
curl -X POST "https://your-url-8000.github.dev/api/get-outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "style": "streetwear",
      "fit": "oversized",
      "body": "athletic",
      "allTags": ["streetwear", "monochrome", "oversized"]
    },
    "occasion": "campus",
    "weather": "mild",
    "num_items": 3,
    "budget_limit": 1500
  }'
```

---

## 🎯 Next Steps

1. **Add your product catalog** to `rag_stylist.py`
2. **Connect to Shopify** using the API endpoints
3. **Build your frontend** (Next.js, React, or plain HTML)
4. **Deploy** when ready (Railway, Render, or keep using Codespaces)

---

## 📚 Learn More

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangChain Docs](https://python.langchain.com/)
- [CLIP Paper](https://openai.com/research/clip)
- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)

---

Built by a 19yo CS student in Egypt. No local installation needed. Works entirely in the cloud.
