import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="EcoScore — Live Sustainability Dashboard", page_icon="🌿")

st.title("🌿 EcoScore Live Dashboard")
st.markdown("Real-time analysis of **product sustainability, health, price, and carbon footprint.**")

# --- User Input ---
product_name = st.text_input("🔍 Enter a product name (e.g., Dove Shampoo):")

# --- Load EPA data ---
@st.cache_data
def load_epa_data():
    url = "https://www.epa.gov/sites/default/files/2020-09/saferchoice-certified-products.csv"
    return pd.read_csv(url)

epa_df = load_epa_data()

# --- Mock price + carbon data ---
price_data = {
    "Dove Shampoo": 5.99,
    "Pantene Shampoo": 6.49,
    "Herbal Essences": 6.29,
    "Aveeno Daily Moisturizer": 8.99,
    "Head & Shoulders": 7.49
}

carbon_data = {
    "Shampoo": 1.8,  # kg CO2e per bottle (est.)
    "Moisturizer": 2.1,
    "Body Wash": 2.5
}

# --- Button click ---
if st.button("Get Live EcoScore"):
    with st.spinner("Fetching data..."):
        # --- Open Beauty Facts API ---
        obf_url = f"https://world.openbeautyfacts.org/cgi/search.pl?search_terms={product_name}&json=1&page_size=1"
        resp = requests.get(obf_url)

        if resp.status_code == 200:
            data = resp.json()
            if data["count"] > 0:
                product = data["products"][0]
                name = product.get("product_name", "Unknown")
                brand = product.get("brands", "Unknown")
                ecoscore = product.get("ecoscore_grade", "n/a")
                ingredients = product.get("ingredients_text", "Not available")
                packaging = product.get("packaging_text", "Not available")

                # --- EPA Certification Check ---
                certified = epa_df[epa_df["Product or Brand Name"].str.contains(brand, case=False, na=False)]
                is_certified = not certified.empty

                # --- Add price & carbon info ---
                est_price = price_data.get(name, price_data.get(brand, "Not available"))
                product_type = "Shampoo" if "shampoo" in name.lower() else "Moisturizer" if "moisturizer" in name.lower() else "Body Wash"
                carbon_intensity = carbon_data.get(product_type, 2.0)

                # --- Display ---
                st.subheader(f"🧴 {name}")
                st.write(f"**Brand:** {brand}")
                st.write(f"**EcoScore:** {ecoscore.upper() if ecoscore != 'n/a' else 'Not Rated'}")
                st.write(f"**Estimated Price:** ${est_price if est_price != 'Not available' else 'N/A'}")
                st.write(f"**Carbon Intensity:** {carbon_intensity} kg CO₂e per bottle")
                st.write(f"**Ingredients:** {ingredients}")
                st.write(f"**Packaging:** {packaging}")

                if "image_url" in product:
                    st.image(product["image_url"], width=200)

                if is_certified:
                    st.success("✅ EPA Safer Choice Certified Product")
                else:
                    st.info("❌ Not EPA-certified (based on database)")

                # --- Scoring ---
                eco_numeric = {"a": 90, "b": 80, "c": 70, "d": 60, "e": 50}.get(ecoscore.lower(), 65 if ecoscore != "n/a" else 50)
                price_score = max(0, 100 - (est_price if isinstance(est_price, (int, float)) else 10) * 10)
                carbon_score = max(0, 100 - (carbon_intensity * 20))
                total_score = int((eco_numeric * 0.5 + price_score * 0.2 + carbon_score * 0.3))

                st.markdown("---")
                st.metric("🌱 Combined EcoScore", f"{total_score}/100")
                st.markdown("""
                **Scoring Formula:**  
                ```
                Total = 0.5 × EcoScore + 0.3 × (100 - 20 × CO₂) + 0.2 × (100 - 10 × Price)
                ```
                """)

            else:
                st.warning("No product found.")
        else:
            st.error("Failed to fetch from Open Beauty Facts API.")

st.markdown("---")
st.caption("Sources: Open Beauty Facts, Open Food Facts, EPA Safer Choice, estimated retail prices.")
