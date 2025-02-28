import json
import os

# Mock database for development
PRODUCT_DATABASE = {
    "pokemon_gold": {
        "title": "Pokemon Gold Version",
        "category": "Video Games & Consoles|Nintendo Game Boy|Games",
        "base_price": 45.99,
        "description": "Pokemon Gold Version for Game Boy Color. The second generation of Pokemon games.",
        "keywords": ["pokemon", "gold", "gameboy", "color", "nintendo", "game"]
    },
    "super_mario_64": {
        "title": "Super Mario 64",
        "category": "Video Games & Consoles|Nintendo 64|Games",
        "base_price": 39.99,
        "description": "Super Mario 64 for Nintendo 64. 3D platformer featuring Mario.",
        "keywords": ["super", "mario", "64", "nintendo", "n64", "3d", "platformer"]
    }
}

PRODUCT_CONDITIONS = {
    "cartridge": [
        {"condition": "complete", "price_multiplier": 2.5},
        {"condition": "cartridge_only", "price_multiplier": 1.0},
        {"condition": "case_manual_only", "price_multiplier": 0.8}
    ],
    "disc": [
        {"condition": "complete", "price_multiplier": 2.0},
        {"condition": "disc_only", "price_multiplier": 0.9},
        {"condition": "case_manual_only", "price_multiplier": 0.7}
    ]
}

def identify_product(filename, extracted_text=None):
    """Try to identify product from filename or extracted text"""
    if not filename:
        return None
        
    filename = filename.lower()
    
    # Check against keywords
    for product_id, product_data in PRODUCT_DATABASE.items():
        keyword_matches = sum(1 for keyword in product_data["keywords"] if keyword.lower() in filename)
        if keyword_matches >= 1:  # At least 1 keyword should match
            return product_id
            
    # Also check text if available
    if extracted_text:
        text = extracted_text.lower()
        for product_id, product_data in PRODUCT_DATABASE.items():
            keyword_matches = sum(1 for keyword in product_data["keywords"] if keyword.lower() in text)
            if keyword_matches >= 2:  # At least 2 keywords should match in OCR text
                return product_id
    
    return None

def get_product_details(product_id, item_type="unknown"):
    """Get product details and price recommendations"""
    if product_id not in PRODUCT_DATABASE:
        return None
        
    product = PRODUCT_DATABASE[product_id].copy()
    
    # Calculate condition-based pricing
    if item_type in PRODUCT_CONDITIONS:
        pricing = []
        for condition in PRODUCT_CONDITIONS[item_type]:
            pricing.append({
                "condition": condition["condition"],
                "price": round(product["base_price"] * condition["price_multiplier"], 2)
            })
        product["pricing"] = pricing
    else:
        product["pricing"] = [{"condition": "unknown", "price": product["base_price"]}]
        
    return product