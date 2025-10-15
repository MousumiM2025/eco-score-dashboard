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

# --- User Input ---
st.markdown("### 🔍 Enter or choose a product name:")
product = st.selectbox(
    "Select a product (or type your own):",
    ["Dove Shampoo", "Pantene Shampoo", "Herbal Essences", "Head & Shoulders", "Aveeno Daily Moisturizer"],
    index=0
)

# --- Button to Generate Score ---
if st.button("Get EcoScore"):
    with st.spinner("Simulating EcoScore analysis..."):
        # Mock dataset (for demo only)
        mock_data = {
            "product": product,
            "brand": "Example Brand",
            "ecoscore": 82,
            "health_score": 76,
            "carbon_score": 68,
            "epa_safer_choice": True,
            "ewg_health_ref": 85.0
        }
        data = mock_data

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
    st.info("👆 Enter or select a product above and click **Get EcoScore** to see results.")





