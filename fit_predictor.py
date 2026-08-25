"""
Fit Predictor — Rules-based size recommendation engine
No AI needed. Runs instantly, free forever.
Optimized for GitHub Codespaces.
"""

import os

# Brand size mapping database (chest in cm)
BRAND_SIZE_MAP = {
    "zara": {
        "S": {"chest": (90, 96), "height": (165, 175), "weight": (55, 68)},
        "M": {"chest": (96, 102), "height": (175, 182), "weight": (68, 78)},
        "L": {"chest": (102, 108), "height": (182, 188), "weight": (78, 88)},
        "XL": {"chest": (108, 116), "height": (188, 195), "weight": (88, 100)},
    },
    "h&m": {
        "S": {"chest": (88, 94), "height": (164, 174), "weight": (54, 67)},
        "M": {"chest": (94, 100), "height": (174, 180), "weight": (67, 77)},
        "L": {"chest": (100, 106), "height": (180, 186), "weight": (77, 87)},
        "XL": {"chest": (106, 114), "height": (186, 194), "weight": (87, 99)},
    },
    "uniqlo": {
        "S": {"chest": (92, 98), "height": (166, 176), "weight": (56, 69)},
        "M": {"chest": (98, 104), "height": (176, 183), "weight": (69, 79)},
        "L": {"chest": (104, 110), "height": (183, 189), "weight": (79, 89)},
        "XL": {"chest": (110, 118), "height": (189, 196), "weight": (89, 101)},
    },
}

# Your brand's size chart (adjust to your actual measurements)
MY_BRAND_SIZES = {
    "S": {"chest": (92, 98), "length": 68, "sleeve": 62},
    "M": {"chest": (98, 104), "length": 70, "sleeve": 64},
    "L": {"chest": (104, 110), "length": 72, "sleeve": 66},
    "XL": {"chest": (110, 118), "length": 74, "sleeve": 68},
    "XXL": {"chest": (118, 126), "length": 76, "sleeve": 70},
}

# Body type adjustments
BODY_ADJUSTMENTS = {
    "slim": -2,
    "athletic": 0,
    "broad": 2,
    "average": 0,
}

# Fit preference adjustments
FIT_ADJUSTMENTS = {
    "oversized": 1,
    "fitted": -1,
    "layered": 0,
    "boxy": 0,
}


def predict_size(known_brand, known_size, height_cm, weight_kg, body_type="average", fit_pref="fitted"):
    """Predict size based on known brand reference."""
    known_brand = known_brand.lower().strip()
    brand_aliases = {
        "h&m": "h&m", "hm": "h&m", "h and m": "h&m",
        "zara": "zara",
        "uniqlo": "uniqlo",
    }
    known_brand = brand_aliases.get(known_brand, known_brand)
    known_size = known_size.upper()

    if known_brand not in BRAND_SIZE_MAP:
        return {"error": f"Unknown brand: {known_brand}. Use: zara, h&m, uniqlo"}

    if known_size not in BRAND_SIZE_MAP[known_brand]:
        return {"error": f"Unknown size: {known_size}"}

    ref_chest_range = BRAND_SIZE_MAP[known_brand][known_size]["chest"]
    ref_chest = (ref_chest_range[0] + ref_chest_range[1]) / 2

    body_adj = BODY_ADJUSTMENTS.get(body_type, 0)
    adjusted_chest = ref_chest + body_adj

    fit_adj = FIT_ADJUSTMENTS.get(fit_pref, 0)

    best_size = None
    best_score = float("inf")

    for size, measurements in MY_BRAND_SIZES.items():
        chest_mid = (measurements["chest"][0] + measurements["chest"][1]) / 2
        diff = abs(adjusted_chest - chest_mid)

        if fit_pref == "oversized" and chest_mid < adjusted_chest:
            diff += 3
        elif fit_pref == "fitted" and chest_mid > adjusted_chest:
            diff += 3

        if diff < best_score:
            best_score = diff
            best_size = size

    size_order = ["S", "M", "L", "XL", "XXL"]
    if best_size in size_order:
        idx = size_order.index(best_size)
        new_idx = max(0, min(len(size_order) - 1, idx + fit_adj))
        recommended = size_order[new_idx]
    else:
        recommended = best_size

    confidence = "high" if best_score < 3 else "medium" if best_score < 6 else "low"

    return {
        "recommended_size": recommended,
        "confidence": confidence,
        "based_on": f"{known_brand.upper()} size {known_size}",
        "estimated_chest_cm": round(adjusted_chest, 1),
        "body_type": body_type,
        "fit_preference": fit_pref,
        "reasoning": f"Based on your {known_brand.upper()} {known_size} fit, we estimate your chest at ~{round(adjusted_chest, 1)}cm. With '{body_type}' body type and '{fit_pref}' preference, we recommend size {recommended}.",
        "your_brand_measurements": MY_BRAND_SIZES.get(recommended, {}),
    }


def predict_size_from_measurements(height_cm, weight_kg, body_type="average", fit_pref="fitted"):
    """Predict size from height/weight when brand reference isn't available."""
    bmi = weight_kg / ((height_cm / 100) ** 2)

    if bmi < 18.5:
        base_chest = 88
    elif bmi < 22:
        base_chest = 96
    elif bmi < 25:
        base_chest = 102
    elif bmi < 28:
        base_chest = 108
    else:
        base_chest = 114

    if height_cm > 185:
        base_chest += 4
    elif height_cm > 180:
        base_chest += 2
    elif height_cm < 170:
        base_chest -= 2

    base_chest += BODY_ADJUSTMENTS.get(body_type, 0)

    best_size = None
    best_score = float("inf")

    for size, measurements in MY_BRAND_SIZES.items():
        chest_mid = (measurements["chest"][0] + measurements["chest"][1]) / 2
        diff = abs(base_chest - chest_mid)

        if fit_pref == "oversized" and chest_mid < base_chest:
            diff += 3
        elif fit_pref == "fitted" and chest_mid > base_chest:
            diff += 3

        if diff < best_score:
            best_score = diff
            best_size = size

    size_order = ["S", "M", "L", "XL", "XXL"]
    if best_size in size_order:
        idx = size_order.index(best_size)
        fit_adj = FIT_ADJUSTMENTS.get(fit_pref, 0)
        new_idx = max(0, min(len(size_order) - 1, idx + fit_adj))
        recommended = size_order[new_idx]
    else:
        recommended = best_size

    confidence = "high" if best_score < 3 else "medium" if best_score < 6 else "low"

    return {
        "recommended_size": recommended,
        "confidence": confidence,
        "estimated_chest_cm": round(base_chest, 1),
        "bmi": round(bmi, 1),
        "body_type": body_type,
        "fit_preference": fit_pref,
        "reasoning": f"Based on your height/weight (BMI {round(bmi, 1)}), we estimate chest ~{round(base_chest, 1)}cm. Recommended: size {recommended} for '{fit_pref}' fit.",
        "your_brand_measurements": MY_BRAND_SIZES.get(recommended, {}),
    }


if __name__ == "__main__":
    print("=" * 50)
    print("FIT PREDICTOR — TESTING")
    print("=" * 50)

    result1 = predict_size("zara", "M", 178, 75, "athletic", "oversized")
    print(f"\nExample 1: {result1['recommended_size']} ({result1['confidence']})")
    print(f"  {result1['reasoning']}")

    result2 = predict_size_from_measurements(182, 82, "broad", "fitted")
    print(f"\nExample 2: {result2['recommended_size']} ({result2['confidence']})")
    print(f"  {result2['reasoning']}")

    result3 = predict_size("h&m", "S", 170, 60, "slim", "oversized")
    print(f"\nExample 3: {result3['recommended_size']} ({result3['confidence']})")
    print(f"  {result3['reasoning']}")
