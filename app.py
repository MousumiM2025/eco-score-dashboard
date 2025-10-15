import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="EcoScore Live", page_icon="🌿")

st.title("🌿 EcoScore Live Product Dashboard")
st.markdown("Compare sustainability, price, and health of products in real-time.")

# --- User Input ---
query = st.text_input("🔍 Search for a product (e.g., Shampoo, Moisturizer):")

# --- Walmart API key ---
API_KEY = st.secrets.get("WALMART_API_KEY", "YOUR_WALMART_API_KEY_HERE")

# --- Load EPA dataset ---
@st.cache_data
def load_epa_data():
    url = "https://www.epa.gov/sites/default/files/2020-09/saferchoice-certified-products.csv"
    return pd.read_csv(url)

epa_df = load_epa_data()

# --- Get Walmart products ---
def search_walmart_products(query):
    url = f"https://api.walmart.com/v3/search?query={query}&format=json&apiKey={API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", [])
        return [
            {
                "name": i.get("name", ""),
                "brand": i.get("brandName", ""),
                "price": i.get("salePrice", "N/A"),
                "image": i.get("mediumImage", ""),
                "url": i.get("productUrl", "")
            }
            for i in items[:10]
        ]
    else:
        st.error("Error fetching data from Walmart API.")
        return []

# --- Search Button ---
if st.button("Search Products"):
    with st.spinner("Fetching products..."):
        products = search_walmart_products(query)

    if products:
        product_names = [p["name"] for p in products]
        selected = st.selectbox("Select a product to analyze:", product_names)

        product = next(p for p in products if p["name"] == selected)
        st.image(product["image"], width=200)
        st.markdown(f"**[{product['name']}]({product['url']})**")
        st.write(f"💰 **Price:** ${product['price']}")
        st.write(f"🏷️ **Brand:** {product['brand']}")

        # --- Open Beauty Facts API ---
        search_url = f"https://world.openbeautyfacts.org/cgi/search.pl?search_terms={product['brand']} {selected}&json=1&page_size=1"
        resp = requests.get(search_url)

        ecoscore, packaging, ingredients = "N/A", "N/A", "N/A"
        if resp.status_code == 200:
            data = resp.json()
            if data["count"] > 0:
                prod = data["products"][0]
                ecoscore = prod.get("ecoscore_grade", "N/A")
                packaging = prod.get("packaging_text", "N/A")
                ingredients = prod.get("ingredients_text", "N/A")

        # --- EPA Certification ---
        certified = epa_df[epa_df["Product or Brand Name"].str.contains(product["brand"], case=False, na=False)]
        is_certified = not certified.empty

        # --- Carbon Estimate ---
        carbon_intensity = 1.8 if "shampoo" in selected.lower() else 2.2

        # --- Display Sustainability ---
        st.subheader("🌿 Sustainability Summary")
        st.write(f"**EcoScore:** {ecoscore.upper() if ecoscore != 'N/A' else ecoscore}")
        st.write(f"**Estimated Carbon Intensity:** {carbon_intensity} kg CO₂e per bottle")
        st.write(f"**Packaging:** {packaging}")
        st.write(f"**Ingredients:** {ingredients}")

        if is_certified:
            st.success("✅ EPA Safer Choice Certified")
        else:
            st.info("❌ Not EPA Certified")

        st.markdown("---")
        st.caption("Sources: Walmart API, Open Beauty Facts, EPA Safer Choice, estimated lifecycle data.")

    else:
        st.warning("No products found. Try a different search keyword.")
