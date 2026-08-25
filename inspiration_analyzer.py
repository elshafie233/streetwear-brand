"""
Inspiration Image Analyzer
Users upload 3-5 images of outfits they love.
Uses CLIP (free, open-source) to analyze visual style.
Optimized for GitHub Codespaces.
"""

import torch
from PIL import Image
import json
import os
from datetime import datetime

# Style vocabulary
STYLE_CONCEPTS = [
    "minimalist fashion", "streetwear style", "y2k aesthetic", "vintage clothing",
    "athleisure wear", "smart casual outfit", "gothic fashion", "preppy style",
    "bohemian fashion", "techwear aesthetic", "normcore style", "grunge outfit",
    "monochrome outfit", "earth tone colors", "neon bright colors", "pastel colors",
    "all black outfit", "white outfit", "beige neutral tones", "bold colorful pattern",
    "oversized baggy fit", "fitted tailored clothing", "cropped short length",
    "boxy wide silhouette", "layered clothing", "skinny tight fit",
    "hoodie sweatshirt", "cargo pants", "graphic printed t-shirt", "denim jeans",
    "oversized blazer", "bomber jacket", "leather jacket", "sneakers shoes",
    "wide leg trousers", "turtleneck sweater", "button up shirt", "puffer jacket",
    "cotton fabric", "denim material", "leather material", "knitwear texture",
    "mesh see-through", "corduroy texture", "linen fabric", "fleece soft material",
    "casual everyday wear", "formal event outfit", "sporty athletic wear",
    "night out party clothes", "work office attire", "festival rave outfit",
]


class InspirationAnalyzer:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()

    def _load_model(self):
        try:
            from transformers import CLIPProcessor, CLIPModel
            print("Loading CLIP model... (first time only, ~500MB)")
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.model.eval()
            print(f"[✓] Model loaded on {self.device}")
        except ImportError:
            print("[!] transformers not installed. Run: pip install transformers torch pillow")
            raise

    def analyze_image(self, image_path, top_k=8):
        if not os.path.exists(image_path):
            return {"error": f"Image not found: {image_path}"}

        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(
            text=STYLE_CONCEPTS, images=image,
            return_tensors="pt", padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)

        probs = probs[0].cpu().numpy()
        top_indices = probs.argsort()[-top_k:][::-1]

        tags = []
        for idx in top_indices:
            tags.append({
                "tag": STYLE_CONCEPTS[idx],
                "confidence": round(float(probs[idx]) * 100, 2),
                "category": self._categorize_tag(STYLE_CONCEPTS[idx])
            })

        profile = self._generate_profile(tags)

        return {
            "image": os.path.basename(image_path),
            "tags": tags,
            "style_profile": profile,
            "analyzed_at": datetime.now().isoformat()
        }

    def analyze_batch(self, image_paths, top_k=8):
        all_results = []
        for path in image_paths:
            print(f"Analyzing: {os.path.basename(path)}")
            result = self.analyze_image(path, top_k)
            all_results.append(result)

        merged = self._merge_profiles(all_results)

        return {
            "individual_results": all_results,
            "unified_profile": merged,
            "images_analyzed": len(image_paths),
            "analyzed_at": datetime.now().isoformat()
        }

    def _categorize_tag(self, tag):
        categories = {
            "aesthetic": ["minimalist", "streetwear", "y2k", "vintage", "athleisure", 
                         "smart casual", "gothic", "preppy", "bohemian", "techwear", "normcore", "grunge"],
            "color": ["monochrome", "earth tone", "neon", "pastel", "all black", "white", "beige", "bold colorful"],
            "fit": ["oversized", "fitted", "cropped", "boxy", "layered", "skinny"],
            "item": ["hoodie", "cargo pants", "graphic", "denim", "blazer", "bomber", 
                    "leather jacket", "sneakers", "trousers", "turtleneck", "shirt", "puffer"],
            "texture": ["cotton", "denim material", "leather material", "knitwear", "mesh", "corduroy", "linen", "fleece"],
            "occasion": ["casual", "formal", "sporty", "night out", "work", "festival"],
        }
        tag_lower = tag.lower()
        for cat, keywords in categories.items():
            if any(kw in tag_lower for kw in keywords):
                return cat
        return "other"

    def _generate_profile(self, tags):
        by_category = {}
        for t in tags:
            cat = t["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(t)

        profile = {
            "primary_aesthetic": None,
            "dominant_colors": [],
            "preferred_fit": None,
            "key_items": [],
            "vibe_summary": ""
        }

        if "aesthetic" in by_category and by_category["aesthetic"]:
            profile["primary_aesthetic"] = by_category["aesthetic"][0]["tag"]
        if "color" in by_category:
            profile["dominant_colors"] = [t["tag"] for t in by_category["color"][:2]]
        if "fit" in by_category and by_category["fit"]:
            profile["preferred_fit"] = by_category["fit"][0]["tag"]
        if "item" in by_category:
            profile["key_items"] = [t["tag"] for t in by_category["item"][:3]]

        parts = []
        if profile["primary_aesthetic"]:
            parts.append(f"{profile['primary_aesthetic'].replace(' fashion', '').replace(' style', '')} vibe")
        if profile["preferred_fit"]:
            parts.append(f"with {profile['preferred_fit'].replace(' fit', '').replace(' clothing', '')} silhouettes")
        if profile["dominant_colors"]:
            parts.append(f"in {', '.join(profile['dominant_colors']).replace(' colors', '').replace(' outfit', '')} tones")

        profile["vibe_summary"] = " ".join(parts) if parts else "Unique eclectic style"
        return profile

    def _merge_profiles(self, results):
        all_tags = []
        for r in results:
            if "tags" in r:
                all_tags.extend(r["tags"])

        tag_scores = {}
        for t in all_tags:
            name = t["tag"]
            if name not in tag_scores:
                tag_scores[name] = {"score": 0, "count": 0, "category": t["category"]}
            tag_scores[name]["score"] += t["confidence"]
            tag_scores[name]["count"] += 1

        averaged = []
        for name, data in tag_scores.items():
            averaged.append({
                "tag": name,
                "avg_confidence": round(data["score"] / data["count"], 2),
                "appearances": data["count"],
                "category": data["category"]
            })

        averaged.sort(key=lambda x: x["avg_confidence"], reverse=True)
        top_tags = [{"tag": t["tag"], "confidence": t["avg_confidence"], "category": t["category"]} 
                    for t in averaged[:10]]

        profile = self._generate_profile(top_tags)

        return {
            "top_tags": averaged[:10],
            "style_profile": profile,
            "images_considered": len(results)
        }

    def match_to_catalog(self, profile, catalog_items):
        profile_tags = set()
        for t in profile.get("top_tags", []):
            profile_tags.add(t["tag"].lower())

        if profile.get("style_profile", {}).get("primary_aesthetic"):
            profile_tags.add(profile["style_profile"]["primary_aesthetic"].lower())

        matches = []
        for item in catalog_items:
            item_tags = set(t.lower() for t in item.get("tags", []))
            overlap = len(profile_tags & item_tags)
            score = overlap / max(len(item_tags), 1)

            if score > 0:
                matches.append({
                    "item": item,
                    "match_score": round(score * 100, 1),
                    "matching_tags": list(profile_tags & item_tags)
                })

        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:5]


if __name__ == "__main__":
    print("=" * 50)
    print("INSPIRATION IMAGE ANALYZER")
    print("=" * 50)

    analyzer = InspirationAnalyzer()

    sample_catalog = [
        {"id": "H001", "name": "Oversized Boxy Hoodie - Black", "tags": ["oversized", "hoodie", "streetwear", "black", "cotton", "boxy"], "price": 550},
        {"id": "C001", "name": "Wide Cargo Pants - Olive", "tags": ["cargo pants", "streetwear", "olive", "wide fit"], "price": 650},
        {"id": "T001", "name": "Cropped Graphic Tee - White", "tags": ["cropped", "graphic tee", "y2k", "white", "casual"], "price": 350},
        {"id": "J001", "name": "Bomber Jacket - Beige", "tags": ["bomber jacket", "smart casual", "beige", "layered"], "price": 850},
        {"id": "S001", "name": "Minimalist Cotton Shirt - White", "tags": ["minimalist", "cotton", "white", "fitted", "work"], "price": 450},
    ]

    demo_profile = {
        "top_tags": [
            {"tag": "oversized baggy fit", "avg_confidence": 92.5, "category": "fit"},
            {"tag": "streetwear style", "avg_confidence": 88.3, "category": "aesthetic"},
            {"tag": "monochrome outfit", "avg_confidence": 85.1, "category": "color"},
            {"tag": "hoodie sweatshirt", "avg_confidence": 79.4, "category": "item"},
            {"tag": "cargo pants", "avg_confidence": 76.2, "category": "item"},
        ],
        "style_profile": {
            "primary_aesthetic": "streetwear style",
            "dominant_colors": ["monochrome outfit"],
            "preferred_fit": "oversized baggy fit",
            "key_items": ["hoodie sweatshirt", "cargo pants"],
            "vibe_summary": "streetwear vibe with oversized silhouettes in monochrome tones"
        }
    }

    print("\n[Demo] User Style Profile:")
    print(f"  Vibe: {demo_profile['style_profile']['vibe_summary']}")

    print("\n[Demo] Matching to catalog...")
    matches = analyzer.match_to_catalog(demo_profile, sample_catalog)

    for m in matches:
        item = m["item"]
        print(f"  → {item['name']} ({item['price']} EGP) — {m['match_score']}% match")
        print(f"    Matching: {', '.join(m['matching_tags'])}")
