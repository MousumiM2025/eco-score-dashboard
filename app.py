import streamlit as st
import requests

st.title("🌎 EcoScore — Environmental & Health Transparency for Products")

# --- user input ---
product = st.text_input("Enter product name:", "Dove Shampoo")

if st.button("Get EcoScore"):
    api_url = f"https://your-api-url/get_score?product_name={product}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            st.error(data["error"])
        else:
            st.subheader(f"Product: {data['product']}")
            st.write(f"**Brand:** {data['brand']}")
            st.metric("EcoScore 🌿", f"{data['ecoscore']}/100")
            st.metric("Health Score ❤️", f"{data['health_score']}/100")
            st.metric("Carbon Impact ⚡", f"{data['carbon_score']}/100")

            if data["epa_safer_choice"]:
                st.success("✅ EPA Safer Choice Certified")
            if data["ewg_health_ref"]:
                st.info(f"EWG adjusted health rating: {data['ewg_health_ref']:.1f}")

# --- footnotes ---
st.markdown("---")
st.markdown("### 📚 Data Sources")
st.markdown("""
This EcoScore combines multiple open datasets and public registries:
- [Open Beauty Facts](https://world.openbeautyfacts.org/) — cosmetics & personal care composition  
- [Open Food Facts](https://world.openfoodfacts.org/) — food & beverage sustainability scores  
- [EWG Skin Deep](https://www.ewg.org/skindeep/) — ingredient health hazard ratings  
- [EPA Safer Choice Database](https://www.epa.gov/saferchoice/products) — verified low-toxicity cleaning products  
All data is used for educational and transparency purposes under open data licenses.
""")

