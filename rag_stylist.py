"""
RAG Stylist — AI Outfit Recommender
Uses your actual product catalog. No hallucinations.
Optimized for GitHub Codespaces.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class RAGStylist:
    def __init__(self, openai_api_key=None):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.vectorstore = None
        self.catalog = []
        self._init_rag()

    def _init_rag(self):
        try:
            from langchain_openai import OpenAIEmbeddings, ChatOpenAI
            from langchain_community.vectorstores import FAISS

            if not self.api_key:
                print("[!] No OpenAI API key found. Set OPENAI_API_KEY in .env")
                print("    Get one at: https://platform.openai.com/api-keys")
                return

            self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7,
                openai_api_key=self.api_key
            )
            print("[✓] RAG Stylist initialized")
        except ImportError:
            print("[!] Required packages not installed.")
            print("    Run: pip install langchain langchain-openai faiss-cpu")
            raise

    def load_catalog(self, catalog_items):
        from langchain.schema import Document

        self.catalog = catalog_items
        documents = []

        for item in catalog_items:
            content = f"""
Product: {item['name']}
Category: {item['category']}
Description: {item['description']}
Style: {', '.join(item.get('tags', []))}
Fit: {item.get('fit', 'regular')}
Color: {item.get('color', 'varied')}
Material: {item.get('material', 'cotton')}
Price: {item['price']} EGP
Available sizes: {', '.join(item.get('sizes', []))}
            """.strip()

            doc = Document(
                page_content=content,
                metadata={
                    "id": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "category": item["category"],
                    "image_url": item.get("image_url", ""),
                    "tags": item.get("tags", [])
                }
            )
            documents.append(doc)

        from langchain_community.vectorstores import FAISS
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        print(f"[✓] Loaded {len(documents)} products into vector store")

    def get_outfit_recommendation(self, user_profile, occasion="casual", weather="mild", 
                                   num_items=3, budget_limit=None):
        if not self.vectorstore:
            return {"error": "Catalog not loaded. Call load_catalog() first."}

        style_tags = user_profile.get("allTags", []) if "allTags" in user_profile else []
        if not style_tags and "style_profile" in user_profile:
            style_tags = [user_profile["style_profile"].get("primary_aesthetic", "")]

        fit_pref = user_profile.get("fit", "fitted") if "fit" in user_profile else "fitted"
        body_type = user_profile.get("body", "average") if "body" in user_profile else "average"

        search_query = f"""
Outfit for {occasion} occasion in {weather} weather.
Style preference: {', '.join(style_tags)}.
Fit preference: {fit_pref}.
Body type: {body_type}.
Looking for {num_items} pieces that work together.
        """.strip()

        retrieved = self.vectorstore.similarity_search(search_query, k=num_items * 3)

        candidates = []
        for doc in retrieved:
            meta = doc.metadata
            if budget_limit and meta["price"] > budget_limit / num_items:
                continue
            candidates.append(meta)

        outfit = self._curate_outfit_with_llm(
            candidates=candidates[:10],
            user_profile=user_profile,
            occasion=occasion,
            weather=weather,
            num_items=num_items,
            budget_limit=budget_limit
        )

        return outfit

    def _curate_outfit_with_llm(self, candidates, user_profile, occasion, weather, num_items, budget_limit):
        candidates_text = "\n".join([
            f"- {c['name']} ({c['category']}) — {c['price']} EGP — Tags: {', '.join(c.get('tags', []))}"
            for c in candidates
        ])

        style_summary = user_profile.get("style", "casual") if isinstance(user_profile, dict) else "casual"
        fit = user_profile.get("fit", "fitted") if isinstance(user_profile, dict) else "fitted"

        prompt = f"""You are an expert fashion stylist for a Gen Z Egyptian streetwear brand.
Your job: curate a cohesive outfit from the available products below.

USER PROFILE:
- Primary style: {style_summary}
- Fit preference: {fit}
- Occasion: {occasion}
- Weather: {weather}
- Budget limit: {budget_limit or 'No limit'} EGP

AVAILABLE PRODUCTS:
{candidates_text}

RULES:
1. Select exactly {num_items} pieces that create a cohesive outfit
2. Pieces must complement each other (colors, styles, occasion-appropriate)
3. Consider the weather — don't recommend heavy layers for hot weather
4. Stay within budget if specified
5. Explain WHY each piece works for this user
6. Suggest shoes/accessories the user likely already owns
7. Write in a friendly, Gen Z tone (confident, not corporate)
8. If you can't make a good outfit with available items, say so honestly

Output ONLY valid JSON in this exact format:
{{
  "outfit_name": "Creative outfit name",
  "pieces": [
    {{
      "id": "product_id",
      "name": "Product Name",
      "price": 550,
      "why": "Why this piece works for the user"
    }}
  ],
  "total_price": 1650,
  "styling_tips": ["Tip 1", "Tip 2"],
  "shoes_suggestion": "What shoes to wear",
  "confidence": "high/medium/low",
  "vibe_check": "One sentence describing the overall look"
}}
"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content

            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                outfit = json.loads(content[json_start:json_end])
            else:
                outfit = json.loads(content)

            outfit["generated_at"] = datetime.now().isoformat()
            outfit["stylist_version"] = "RAG-v1"
            return outfit
        except Exception as e:
            return {
                "error": f"LLM curation failed: {str(e)}",
                "fallback": "Please try again with different parameters."
            }

    def ask_stylist(self, question, user_profile=None):
        if not self.vectorstore:
            return {"error": "Catalog not loaded."}

        retrieved = self.vectorstore.similarity_search(question, k=5)
        context = "\n".join([doc.page_content for doc in retrieved])

        style_context = ""
        if user_profile:
            style_context = f"User style: {user_profile.get('style', 'casual')}, fit: {user_profile.get('fit', 'fitted')}"

        prompt = f"""You are the AI stylist for an Egyptian streetwear brand.
You ONLY recommend products from the catalog below. Never suggest items not listed.

{style_context}

AVAILABLE PRODUCTS:
{context}

USER QUESTION: {question}

Answer helpfully. If the question is about something not in catalog, be honest and suggest alternatives from catalog.
Keep it Gen Z friendly. One or two paragraphs max.
"""

        response = self.llm.invoke(prompt)
        return {
            "answer": response.content,
            "referenced_products": [doc.metadata["name"] for doc in retrieved],
            "asked_at": datetime.now().isoformat()
        }

    def save_catalog_vectors(self, path="catalog_vectors"):
        if self.vectorstore:
            self.vectorstore.save_local(path)
            print(f"[✓] Vectors saved to {path}")

    def load_catalog_vectors(self, path="catalog_vectors"):
        from langchain_community.vectorstores import FAISS
        from langchain_openai import OpenAIEmbeddings

        if os.path.exists(path):
            self.vectorstore = FAISS.load_local(path, self.embeddings)
            print(f"[✓] Vectors loaded from {path}")
        else:
            print(f"[!] No saved vectors found at {path}")


if __name__ == "__main__":
    print("=" * 50)
    print("RAG STYLIST — AI OUTFIT RECOMMENDER")
    print("=" * 50)

    sample_catalog = [
        {
            "id": "H001", "name": "Oversized Boxy Hoodie - Black", "category": "tops",
            "description": "Heavyweight 400gsm Egyptian cotton. Drop shoulder, boxy silhouette. Ribbed cuffs.",
            "tags": ["oversized", "hoodie", "streetwear", "black", "cotton", "boxy"],
            "price": 550, "sizes": ["S", "M", "L", "XL"],
            "fit": "oversized", "color": "black", "material": "cotton", "image_url": "/images/h001.jpg"
        },
        {
            "id": "C001", "name": "Wide Cargo Pants - Olive", "category": "bottoms",
            "description": "Cotton twill cargo pants with 6 pockets. Wide leg, elastic waist.",
            "tags": ["cargo pants", "streetwear", "olive", "wide fit"],
            "price": 650, "sizes": ["S", "M", "L", "XL"],
            "fit": "oversized", "color": "olive", "material": "cotton twill", "image_url": "/images/c001.jpg"
        },
        {
            "id": "T001", "name": "Cropped Graphic Tee - White", "category": "tops",
            "description": "Cropped boxy tee with original Cairo graphic. 220gsm cotton.",
            "tags": ["cropped", "graphic tee", "y2k", "white", "cairo", "boxy"],
            "price": 350, "sizes": ["S", "M", "L"],
            "fit": "boxy", "color": "white", "material": "cotton", "image_url": "/images/t001.jpg"
        },
        {
            "id": "J001", "name": "Bomber Jacket - Beige", "category": "outerwear",
            "description": "Lightweight nylon bomber. Ribbed collar/cuffs. Relaxed fit.",
            "tags": ["bomber jacket", "smart casual", "beige", "layered", "nylon"],
            "price": 850, "sizes": ["S", "M", "L", "XL"],
            "fit": "relaxed", "color": "beige", "material": "nylon", "image_url": "/images/j001.jpg"
        },
        {
            "id": "S001", "name": "Minimalist Cotton Shirt - White", "category": "tops",
            "description": "Clean button-up in premium Egyptian cotton. Regular fit. Hidden placket.",
            "tags": ["minimalist", "cotton", "white", "fitted", "smart casual", "clean"],
            "price": 450, "sizes": ["S", "M", "L", "XL"],
            "fit": "regular", "color": "white", "material": "cotton", "image_url": "/images/s001.jpg"
        },
        {
            "id": "P001", "name": "Baggy Denim Jeans - Light Wash", "category": "bottoms",
            "description": "Relaxed baggy denim with light wash. Heavyweight 14oz denim. Y2K inspired wide leg.",
            "tags": ["baggy", "denim", "y2k", "light wash", "wide leg", "streetwear"],
            "price": 700, "sizes": ["S", "M", "L", "XL"],
            "fit": "baggy", "color": "light blue", "material": "denim", "image_url": "/images/p001.jpg"
        },
    ]

    stylist = RAGStylist()
    if stylist.vectorstore:
        stylist.load_catalog(sample_catalog)

        user = {
            "style": "streetwear", "fit": "oversized", "body": "athletic",
            "budget": "mid_range",
            "allTags": ["streetwear", "monochrome", "oversized", "campus", "hoodie_lover", "mid_range", "athletic"]
        }

        outfit = stylist.get_outfit_recommendation(
            user_profile=user, occasion="campus", weather="mild",
            num_items=3, budget_limit=1500
        )
        print(json.dumps(outfit, indent=2))
    else:
        print("[!] Set OPENAI_API_KEY in .env to run live examples")
        print("    export OPENAI_API_KEY='sk-your-key-here'")
