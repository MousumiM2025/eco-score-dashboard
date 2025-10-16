import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ecosscore_data_2023.csv")  # <-- ensure filename matches your CSV
    return df

df = load_data()

st.set_page_config(page_title="EcoScore Dashboard", page_icon="🌿", layout="wide")

# -------------------------------
# App Title
# -------------------------------
st.title("🌿 EcoScore Dashboard — Sustainable Product Insights (2023 Baseline price)")
st.markdown("""
Compare sustainability, carbon intensity, and health impact of everyday consumer products.
Select a **category** and one or more **products** to explore details and compare their scores.
""")

# -------------------------------
# Dropdown filters
# -------------------------------
categories = df["Category"].unique()
selected_category = st.selectbox("Select a Category:", sorted(categories))

filtered_df = df[df["Category"] == selected_category]

# Multi-select for product comparison
selected_products = st.multiselect(
    "Select one or more Products to Compare:",
    sorted(filtered_df["Product"].unique()),
    default=sorted(filtered_df["Product"].unique())[:2]  # preselect first two
)

if not selected_products:
    st.warning("Please select at least one product to compare.")
    st.stop()

compare_df = filtered_df[filtered_df["Product"].isin(selected_products)]

# -------------------------------
# Comparison Table
# -------------------------------
st.markdown("### 🧾 Product Comparison Table")
st.dataframe(
    compare_df[[
        "Product", "Brand", "Price_USD", "EcoScore",
        "Carbon_Intensity_gCO2eq", "Packaging_Type", "Main_Ingredients"
    ]].rename(columns={
        "Product": "Product Name",
        "Brand": "Brand",
        "Price_USD": "Price (USD)",
        "EcoScore": "EcoScore",
        "Carbon_Intensity_gCO2eq": "Carbon Intensity (gCO₂e)",
        "Packaging_Type": "Packaging",
        "Main_Ingredients": "Main Ingredients"
    }),
    use_container_width=True,
    hide_index=True
)

# -------------------------------
# Scatter Chart — EcoScore vs Price
# -------------------------------
st.markdown("### 📊 EcoScore vs Price (USD)")

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

**Data Sources:**  
EWG Database, Open Beauty Facts, Walmart Product Data (2023 baseline price), Company Sustainability Reports.

**Note:** Prices are based on 2023 U.S. retail averages.
""")

st.caption("Developed by EcoScore.AI — prototype for sustainable consumer transparency.")
