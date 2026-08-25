"""
Fashion Brand API Server
Ties all modules together into a single backend.
Optimized for GitHub Codespaces.

Run: uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
Codespaces auto-forwards port 8000. Check the Ports tab for your public URL.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import your modules
from fit_predictor import predict_size, predict_size_from_measurements
from trend_scraper import TrendScraper
from inspiration_analyzer import InspirationAnalyzer
from rag_stylist import RAGStylist

app = FastAPI(
    title="AI Streetwear Brand API",
    description="AI-powered style analysis, size prediction, and outfit recommendation",
    version="1.0"
)

# CORS — allow your frontend to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== MODELS ========
class SizePredictionRequest(BaseModel):
    known_brand: Optional[str] = None
    known_size: Optional[str] = None
    height_cm: int
    weight_kg: int
    body_type: str = "average"
    fit_preference: str = "fitted"

class StyleQuizResult(BaseModel):
    style: str
    fit: str
    body: str
    budget: str
    allTags: List[str]

class OutfitRequest(BaseModel):
    user_profile: dict
    occasion: str = "casual"
    weather: str = "mild"
    num_items: int = 3
    budget_limit: Optional[int] = None

class StylistQuestion(BaseModel):
    question: str
    user_profile: Optional[dict] = None

# ======== GLOBALS ========
stylist = None
trend_scraper = None
inspiration_analyzer = None

@app.on_event("startup")
async def startup():
    """Initialize AI models on server start."""
    global stylist, trend_scraper, inspiration_analyzer

    try:
        stylist = RAGStylist()
        print("[✓] Stylist initialized")
    except Exception as e:
        print(f"[!] Stylist init failed: {e}")

    trend_scraper = TrendScraper()

    try:
        inspiration_analyzer = InspirationAnalyzer()
        print("[✓] Inspiration analyzer initialized")
    except Exception as e:
        print(f"[!] Inspiration analyzer init failed: {e}")

# ======== ENDPOINTS ========

@app.get("/")
def root():
    return {
        "status": "AI Streetwear Brand API is running",
        "version": "1.0",
        "docs": "/docs",
        "environment": "GitHub Codespaces"
    }

@app.post("/api/predict-size")
def api_predict_size(req: SizePredictionRequest):
    """Predict size based on known brand or body measurements."""
    if req.known_brand and req.known_size:
        result = predict_size(
            known_brand=req.known_brand,
            known_size=req.known_size,
            height_cm=req.height_cm,
            weight_kg=req.weight_kg,
            body_type=req.body_type,
            fit_pref=req.fit_preference
        )
    else:
        result = predict_size_from_measurements(
            height_cm=req.height_cm,
            weight_kg=req.weight_kg,
            body_type=req.body_type,
            fit_pref=req.fit_preference
        )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/analyze-inspiration")
async def api_analyze_inspiration(files: List[UploadFile] = File(...)):
    """Upload 3-5 inspiration images, get style analysis."""
    if not inspiration_analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")

    if len(files) < 1 or len(files) > 5:
        raise HTTPException(status_code=400, detail="Upload 1-5 images")

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    paths = []

    for file in files:
        path = os.path.join(upload_dir, f"{datetime.now().timestamp()}_{file.filename}")
        with open(path, "wb") as f:
            f.write(await file.read())
        paths.append(path)

    result = inspiration_analyzer.analyze_batch(paths)

    for path in paths:
        os.remove(path)

    return result

@app.post("/api/get-outfit")
def api_get_outfit(req: OutfitRequest):
    """Get AI-curated outfit recommendation."""
    if not stylist or not stylist.vectorstore:
        raise HTTPException(status_code=503, detail="Stylist not initialized or catalog not loaded")

    result = stylist.get_outfit_recommendation(
        user_profile=req.user_profile,
        occasion=req.occasion,
        weather=req.weather,
        num_items=req.num_items,
        budget_limit=req.budget_limit
    )
    return result

@app.post("/api/ask-stylist")
def api_ask_stylist(req: StylistQuestion):
    """Free-form chat with the AI stylist."""
    if not stylist or not stylist.vectorstore:
        raise HTTPException(status_code=503, detail="Stylist not initialized")

    result = stylist.ask_stylist(req.question, req.user_profile)
    return result

@app.get("/api/trends")
def api_trends():
    """Get current fashion trend report."""
    if not trend_scraper:
        raise HTTPException(status_code=503, detail="Trend scraper not initialized")

    report = trend_scraper.run_full_scan()
    return report

@app.get("/api/health")
def health_check():
    """Check if all services are running."""
    return {
        "status": "healthy",
        "services": {
            "fit_predictor": True,
            "trend_scraper": trend_scraper is not None,
            "inspiration_analyzer": inspiration_analyzer is not None,
            "rag_stylist": stylist is not None and stylist.vectorstore is not None
        },
        "timestamp": datetime.now().isoformat()
    }

# ======== RUN ========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
