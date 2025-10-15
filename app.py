#import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(
    page_title="EcoScore Dashboard",
    page_icon="🌿",
    layout="centered",
)

# --- Header ---
st.title("🌿 EcoScore — Product Environmental & Health Transparency")
st.markdown("Understand the **real impact** of everyday products — from ingredients to packaging and certifications.")

# --- Mock product database ---
sample_products = {
    "Dove Shampoo": {
        "brand": "Dove",
        "ecoscore": 78,
        "health_score": 72,
        "carbon_score": 65,
        "price_usd": 6.49,
        "ingredients": ["Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine", "Fragrance"],
        "packaging": "Plastic bottle (HDPE, recyclable)",
        "epa_safer_choice": False,
        "ewg_health_ref": 80.0
    },
    "Pantene Shampoo": {
        "brand": "Pantene",
        "ecoscore": 70,
        "health_score": 68,
        "carbon_score": 62,
        "price_usd": 5.99,
        "ingredients": ["Water", "Sodium Lauryl Sulfate", "Dimethicone", "Fragrance"],
        "packaging": "Plastic bottle (PET, partially recyclable)",
        "epa_safer_choice": False,
        "ewg_health_ref": 75.0
    },
    "Herbal Essences": {
        "brand": "Herbal Essences",
        "ecoscore": 84,
        "health_score": 80,
        "carbon_score": 72,
        "price_usd": 7.49,
        "ingredients": ["Aloe", "Coconut Extract", "Citric Acid", "Fragrance"],
        "packaging": "Recycled plastic bottle (25% PCR)",
        "epa_safer_choice": True,
        "ewg_health_ref": 88.0
    },
    "Head & Shoulders": {
        "brand": "Head & Shoulders",
        "ecoscore": 66,
        "health_score": 60,
        "carbon_score": 58,
        "price_usd": 6.99,
        "ingredients": ["Pyrithione Zinc", "Sodium Lauryl Sulfate", "Fragrance"],
        "packaging": "Plastic bottle (HDPE, recyclable)",
        "epa_safer_choice": False,
        "ewg_health_ref": 70.0
    },
    "Aveeno Daily Moisturizer": {
        "brand": "Aveeno",
        "ecoscore": 90,
        "health_score": 85,
        "carbon_score": 80,
        "price_usd": 8.99,
        "ingredients": ["Oatmeal Extract", "Glycerin", "Dimethicone", "Water"],
        "packaging": "Plastic tube (HDPE, partially recyclable)",
        "epa_safer_choice": True,
        "ewg_health_ref": 92.0
    },
    "Native Shampoo": {
        "brand": "Native",
        "ecoscore": 88,
        "health_score": 90,
        "carbon_score": 78,
        "price_usd": 9.99,
        "ingredients": ["Coconut Oil", "Cleansing Salt", "Coconut Water", "Fragrance (natural)"],
        "packaging": "Recycled aluminum bottle (fully recyclable)",
        "epa_safer_choice": True,
        "ewg_health_ref": 95.0
    },
    "Suave Essentials": {
        "brand": "Suave",
        "ecoscore": 62,
        "health_score": 55,
        "carbon_score": 60,
        "price_usd": 3.99,
        "ingredients": ["Water", "Sodium Laureth Sulfate", "Fragrance", "Citric Acid"],
        "packaging": "Plastic bottle (PET, recyclable)",
        "epa_safer_choice": False,
        "ewg_health_ref": 68.0
    },
    "The Body Shop Ginger Shampoo": {
        "brand": "The Body Shop",
        "ecoscore": 92,
        "health_score": 88,
        "carbon_score": 84,
        "price_usd": 12.00,
        "ingredients": ["Ginger Root Extract", "Aloe Vera", "Panthenol"],
        "packaging": "Recycled plastic bottle (100% PCR)",
        "epa_safer_choice": True,
        "ewg_health_ref": 93.0
    },
    "L’Oréal Elvive": {
        "brand": "L’Oréal",
        "ecoscore": 74,
        "health_score": 70,
        "carbon_score": 66,
        "price_usd": 6.79,
        "ingredients": ["Water", "Cocamidopropyl Betaine", "Dimethicone", "Fragrance"],
        "packaging": "Plastic bottle (PET, partially recyclable)",
        "epa_safer_choice": False,
        "ewg_health_ref": 78.0
    },
    "SheaMoisture Coconut & Hibiscus": {
        "brand": "SheaMoisture",
        "ecoscore": 89,
        "health_score": 92,
        "carbon_score": 82,
        "price_usd": 11.49,
        "ingredients": ["Coconut Oil", "Hibiscus Flower Extract", "Shea Butter", "Aloe Vera"],
        "packaging": "Plastic jar (HDPE, recyclable)",
        "epa_safer_choice": True,
        "ewg_health_ref": 96.0
    }
}

# --- Product Selection ---
st.markdown("### 🔍 Choose one or more products to compare:")
selected_products = st.multiselect(
    "Select products:",
    list(sample_products.keys()),
    default=["Dove Shampoo"]
)

manual_product = st.text_input("Or enter a custom product name (optional):", "")

if st.button("Get EcoScore"):
    with st.spinner("Analyzing sustainability data..."):
        results = []
        for product in selected_products:
            data = sample_products[product]
            data["product"] = product
            results.append(data)

        if manual_product:
            results.append({
                "product": manual_product,
                "brand": "Unknown",
                "ecoscore": 75,
                "health_score": 70,
                "carbon_score": 65,
                "price_usd": 7.00,
                "ingredients": ["N/A"],
                "packaging": "Unknown",
                "epa_safer_choice": False,
                "ewg_health_ref": 78.0
            })

        df = pd.DataFrame(results)

    # --- Individual

