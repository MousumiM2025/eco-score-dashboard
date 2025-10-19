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
product = st.text_input("🔍 Enter a product name:", "Dove Shampoo")

if st.button("Get EcoScore"):
    api_url = f"https://your-api-url/get_score?product_name={product}"
    with st.spinner("Fetching and analyzing data..."):
        response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            st.error(data["error"])
        else:
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
            st.markdown("### 📚 Data Sources")
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
        st.error("⚠️ API connection failed. Please try again later.")

