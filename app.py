import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ecoscore_data_2023.csv")
    return df

df = load_data()

st.set_page_config(page_title="EcoScore Dashboard", page_icon="🌿", layout="wide")

# -------------------------------
# App Title
# -------------------------------
st.title("🌿 EcoScore Dashboard — Product Sustainability Insights (2023 Baseline)")
st.markdown("""
Compare sustainability, carbon intensity, and health impact of everyday consumer products.
Select a **category** and a **product** to explore details and see how it ranks against others.
""")

# -------------------------------
# Dropdown filters
# -------------------------------
categories = df["Category"].unique()
selected_category = st.selectbox("Select a Category:", sorted(categories))

filtered_df = df[df["Category"] == selected_category]

products = filtered_df["Product"].unique()
selected_product = st.selectbox("Select a Product:", sorted(products))

product_info = filtered_df[filtered_df["Product"] == selected_product].iloc[0]

# -------------------------------
# Product Information
# -------------------------------
st.subheader(f"🔍 {selected_product} — {product_info['Brand']}")
col1, col2, col3, col4 = st.columns(4)

col1.metric("💲 Price (USD)", f"${product_info['Price_USD']:.2f}")
col2.metric("🌱 EcoScore", f"{product_info['EcoScore']}/100")
col3.metric("♻️ Carbon Intensity", f"{product_info['Carbon_Intensity_gCO2eq']} gCO₂e")
col4.metric("🧴 Packaging", product_info["Packaging_Type"])

st.markdown(f"**Main Ingredients:** {product_info['Main_Ingredients']}")

# -------------------------------
# Scatter Chart — EcoScore vs Price
# -------------------------------
st.markdown("### 💬 Category Comparison: EcoScore vs Price (USD)")

fig = px.scatter(
    filtered_df,
    x="Price_USD",
    y="EcoScore",
    text="Product",
    color="Brand",
    size="Carbon_Intensity_gCO2eq",
    hover_data=["Main_Ingredients", "Packaging_Type"],
    title=f"{selected_category}: EcoScore vs Price (2023)",
)

fig.update_traces(textposition="top center")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Footnote and Transparency
# -------------------------------
st.markdown("---")
st.markdown("""
### 📘 Scoring Criteria & Data Sources
**EcoScore** combines weighted indicators:
- 🌿 Ingredient safety & biodegradability (40%)
- ⚡ Carbon intensity during production (30%)
- ♻️ Packaging sustainability (20%)
- 💰 Price fairness index (10%)

**Data Sources:** EWG Database, Open Beauty Facts, Walmart Product Data (2023 baseline pricing), Company Sustainability Reports.
""")

st.caption("Developed by EcoScore.AI — prototype for sustainable consumer transparency.")

