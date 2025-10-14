import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

# -----------------------------
# 🌍 APP CONFIG
# -----------------------------
st.set_page_config(
    page_title="EcoScore Dashboard 🌱",
    page_icon="🌿",
    layout="centered"
)

st.title("🌿 EcoScore Dashboard")
st.markdown("Enter any shampoo or cosmetic product to see its **Eco, Health, and Price Scores**!")

# -----------------------------
# 🔍 USER INPUT
# -----------------------------
product_name = st.text_input("🔎 Enter product name (e.g., 'Pantene Shampoo')")

# -----------------------------
# ⚙️ FUNCTION: FETCH PRODUCT DATA
# -----------------------------
def fetch_product_data(name):
    url = f"https://world.openbeautyfacts.org/cgi/search.pl?search_terms={name}&json=1"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data["count"] > 0:
            return data["products"][0]
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


# -----------------------------
# 🧮 FUNCTION: COMPUTE ECOSCORE
# -----------------------------
def compute_scores(product):
    """Simple scoring mockup based on available info"""
    packaging = 20
    eco_ingredients = 15
    health = 10
    transparency = 10
    innovation = 8
    price = 10

    pname = product.get("product_name", "Unknown Product")
    ingred = product.get("ingredients_text", "").lower()

    # Ingredient-based simple scoring logic
    if any(word in ingred for word in ["sodium laureth sulfate", "sls", "paraben", "fragrance"]):
        health -= 3
        eco_ingredients -= 3

    if "recycled" in ingred or "plant" in ingred or "organic" in ingred:
        eco_ingredients += 2

    # Normalize total
    total = packaging + eco_ingredients + health + transparency + innovation + price

    return {
        "packaging": packaging,
        "eco_ingredients": eco_ingredients,
        "health": health,
        "transparency": transparency,
        "innovation": innovation,
        "price": price,
        "total": total,
        "grade": "A" if total > 85 else "B" if total > 75 else "C" if total > 65 else "D"
    }


# -----------------------------
# 🚀 MAIN APP LOGIC
# -----------------------------
if product_name:
    with st.spinner("Fetching data..."):
        product = fetch_product_data(product_name)

    if product:
        st.success(f"✅ Found: **{product.get('product_name', 'Unknown Product')}**")
        st.image(product.get("image_url", ""), width=150)
        st.markdown(f"**Brand:** {product.get('brands', 'N/A')}")
        st.markdown(f"**Ingredients:** {product.get('ingredients_text', 'No ingredient info available')[:300]}...")

        scores = compute_scores(product)
        st.subheader(f"🌱 EcoScore: {scores['total']}/100 — Grade {scores['grade']}")

        # Visualization
        categories = ["Packaging", "Eco Ingredients", "Health", "Transparency", "Innovation", "Price"]
        values = [scores["packaging"], scores["eco_ingredients"], scores["health"],
                  scores["transparency"], scores["innovation"], scores["price"]]

        fig = go.Figure(go.Bar(
            x=categories,
            y=values,
            text=[f"{v}" for v in values],
            textposition="auto"
        ))
        fig.update_layout(
            yaxis=dict(range=[0, 25]),
            title="EcoScore Breakdown by Category"
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No data found for that product. Try a different name.")
else:
    st.info("Enter a product name above to begin.")
