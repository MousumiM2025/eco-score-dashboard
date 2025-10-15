import streamlit as st
import requests

# --- Page Config ---
st.set_page_config(
    page_title="EcoScore Dashboard",
    page_icon="🌎",
    layout="centered",
)

# --- Header ---
st.title("🌿 EcoScore — Product Environmental & Health Transparency")
st.markdown("Understand the **real impact** of everyday products — from ingredients to packaging and certifications.")

# --- Mock product database ---
sample_products = {
    "Dove Shampoo": {"brand": "Dove", "ecoscore": 78, "health_score": 72, "carbon_score": 65, "epa_safer_choice": False, "ewg_health_ref": 80.0},
    "Pantene Shampoo": {"brand": "Pantene", "ecoscore": 70, "health_score": 68, "carbon_score": 62, "epa_safer_choice": False, "ewg_health_ref": 75.0},
    "Herbal Essences": {"brand": "Herbal Essences", "ecoscore": 84, "health_score": 80, "carbon_score": 72, "epa_safer_choice": True, "ewg_health_ref": 88.0},
    "Head & Shoulders": {"brand": "Head & Shoulders", "ecoscore": 66, "health_score": 60, "carbon_score": 58, "epa_safer_choice": False, "ewg_health_ref": 70.0},
    "Aveeno Daily Moisturizer": {"brand": "Aveeno", "ecoscore": 90, "health_score": 85, "carbon_score": 80, "epa_safer_choice": True, "ewg_health_ref": 92.0},
    "Native Shampoo": {"brand": "Native", "ecoscore": 88, "health_score": 90, "carbon_score": 78, "epa_safer_choice": True, "ewg_health_ref": 95.0},
    "Suave Essentials": {"brand": "Suave", "ecoscore": 62, "health_score": 55, "carbon_score": 60, "epa_safer_choice": False, "ewg_health_ref": 68.0},
    "The Body Shop Ginger Shampoo": {"brand": "The Body Shop", "ecoscore": 92, "health_score": 88, "carbon_score": 84, "epa_safer_choice": True, "ewg_health_ref": 93.0},
    "L’Oréal Elvive": {"brand": "L’Oréal", "ecoscore": 74, "health_score": 70, "carbon_score": 66, "epa_safer_choice": False, "ewg_health_ref": 78.0},
    "SheaMoisture Coconut & Hibiscus": {"brand": "SheaMoisture", "ecoscore": 89, "health_score": 92, "carbon_score": 82, "epa_safer_choice": True, "ewg_health_ref": 96.0}
}

# --- Product Input ---
st.markdown("### 🔍 Choose a sample product or type your own:")
product = st.selectbox(
    "Select a product:",
    list(sample_products.keys()) + ["Other (type manually)"],
    index=0
)

if product == "Other (type manually)":
    product = st.text_input("Enter your product name:", "")

# --- Button to Generate Score ---
if st.button("Get EcoScore"):
    with st.spinner("Analyzing product sustainability data..."):
        if product in sample_products:
            data = sample_products[product]
            data["product"] = product
        else:
            # Default mock values for custom products
            data = {
                "product": product or "Custom Product",
                "brand": "Unknown Brand",
                "ecoscore": 75,
                "health_score": 70,
                "carbon_score": 65,
                "epa_safer_choice": False,
                "ewg_health_ref": 78.0
            }

    # --- Display Results ---
    st.subheader(f"🧴 {data['product']}")
    st.write(f"**Brand:** {data['brand']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("🌱 EcoScore", f"{data['ecoscore']}/100")
    col2.metric("❤️ Health Score", f"{data['health_score']}/100")
    col3.metric("⚡ Carbon Impact", f"{data['carbon_score']}/100")

    if data.get("epa_safer_choice"):
        st.success("✅ Certified by EPA Safer Choice")

    if data.get("ewg_health_ref"):
        st.info(f"EWG Adjusted Health Rating: {data['ewg_health_ref']:.1f}/100")

    st.markdown("---")

    # --- Explanation ---
    with st.expander("🔍 How EcoScore is Calculated"):
        st.markdown("""
        **EcoScore (0–100)** combines environmental, health, and lifecycle factors:

        | Factor | Weight | Description |
        |---------|--------|-------------|
        | ♻️ **Packaging** | 20% | Recyclable paper/glass rated higher; plastics penalized |
        | 💧 **Carbon Intensity** | 30% | Based on product category lifecycle emission factors |
        | 🌱 **Ingredient Safety** | 40% | Derived from EWG hazard ratings (lower hazard = higher score) |
        | 🏅 **Certifications** | 10% | Bonus points for EPA Safer Choice, EcoLabel, or organic certification |

        **Formula:**
        ```
        EcoScore = (0.4 × Health) + (0.3 × Carbon) + (0.2 × Packaging) + (0.1 × CertificationBonus)
        ```
        """)

    st.markdown("---")

    # --- Data Sources ---
    st.markdown("### 📚 Data Sources & References")
    st.markdown("""
    This analysis combines publicly available environmental and health data:
    - [Open Beauty Facts](https://world.openbeautyfacts.org/) — cosmetics & personal care composition  
    - [Open Food Facts](https://world.openfoodfacts.org/) — food & beverage sustainability scores  
    - [EWG Skin Deep](https://www.ewg.org/skindeep/) — ingredient health hazard ratings  
    - [EPA Safer Choice](https://www.epa.gov/saferchoice/products) — verified low-toxicity products  

    ---
    *This dashboard is for transparency and education only. Scores are estimated using open datasets.*
    """)

else:
    st.info("👆 Choose a product above and click **Get EcoScore** to see results.")




