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
        "
