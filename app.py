import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------
# PAGE CONFIG & LOGO
# --------------------------
st.set_page_config(page_title="EcoScore Dashboard", layout="wide")

st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Leaf_icon_02.svg/512px-Leaf_icon_02.svg.png",
    width=100,
)
st.title("🌱 EcoScore Dashboard — Product Sustainability Insights")
st.markdown("Explore how personal care products perform on environmental sustainability metrics.")

# --------------------------
# LOAD DATA
# --------------------------
try:
    df = pd.read_csv("ecoscore_data_extended.csv")
except FileNotFoundError:
    st.error("❌ File 'ecoscore_data_extended.csv' not found. Please upload it or check the path.")
    st.stop()

# --------------------------
# CLEAN + NORMALIZE COLUMNS
# --------------------------
df.columns = df.columns.str.strip().str.lower()

def find_col(possible_names):
    """Find a column name by scanning possible matches."""
    for name in possible_names:
        if name.lower() in df.columns:
            return name.lower()
    return None

col_product = find_col(["product", "product_name", "item", "name"])
col_category = find_col(["category", "type", "segment"])
col_price = find_col(["price_usd", "price", "cost"])
col_ecoscore = find_col(["ecoscore", "eco_score", "score"])
col_carbon = find_col(["carbon_intensity_gco2e", "carbon_intensity", "emissions", "co2_intensity"])
col_packaging = find_col(["packaging", "package_type", "material"])

# --------------------------
# DROPDOWN FILTERS
# --------------------------
st.markdown("### 🔎 Select a Product Category or Product Name")

if col_category:
    category_list = sorted(df[col_category].dropna().unique())
    selected_category = st.selectbox("Select Category", ["All"] + category_list)
else:
    selected_category = "All"

if col_product:
    if selected_category != "All":
        filtered_df = df[df[col_category] == selected_category]
    else:
        filtered_df = df
    product_list = sorted(filtered_df[col_product].dropna().unique())
    selected_product = st.selectbox("Select Product", ["All"] + product_list)
else:
    selected_product = "All"
    filtered_df = df

# Filter data
if selected_category != "All":
    df_selected = df[df[col_category] == selected_category]
else:
    df_selected = df.copy()

if selected_product != "All":
    df_selected = df_selected[df_selected[col_product] == selected_product]

# --------------------------
# DATA DISPLAY
# --------------------------
st.markdown("### 📊 Selected Products")
try:
    cols_to_show = [c for c in [col_product, col_category, col_price, col_ecoscore, col_carbon, col_packaging] if c]
    st.dataframe(
        df_selected[cols_to_show].style.format(
            {
                col_price: "${:,.2f}",
                col_carbon: "{:.1f} gCO₂e",
            }
        ),
        use_container_width=True,
    )
except KeyError:
    st.warning("⚠️ Some expected columns were not found. Please check column names in your CSV.")

# --------------------------
# SCATTER PLOTS
# --------------------------
st.markdown("### 📈 Visual Insights")

col1, col2 = st.columns(2)

with col1:
    if col_ecoscore and col_price:
        fig1 = px.scatter(
            df_selected,
            x=col_ecoscore,
            y=col_price,
            color=col_category,
            hover_data=[col_product],
            title="EcoScore vs Price (Sustainability vs Cost)",
            trendline="ols",
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("EcoScore or Price column not found.")

with col2:
    if col_ecoscore and col_carbon:
        fig2 = px.scatter(
            df_selected,
            x=col_ecoscore,
            y=col_carbon,
            color=col_category,
            hover_data=[col_product],
            title="EcoScore vs Carbon Intensity (Sustainability vs Emissions)",
            trendline="ols",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("EcoScore or Carbon Intensity column not found.")

# --------------------------
# EXPLANATION
# --------------------------
st.markdown("""
---
### ♻️ Understanding Carbon Intensity

Products with **higher carbon intensity** often have:
- 🌍 Long supply chains or imported raw materials  
- ⚙️ Energy-intensive manufacturing or chemical processes  
- 🧴 Non-recyclable or fossil-based packaging  
- 💰 Lower EcoScore due to higher lifecycle emissions  

Improving packaging recyclability, switching to renewable energy, and optimizing transport can
**increase EcoScore and lower total CO₂ emissions**.
""")

# --------------------------
# FOOTER
# --------------------------
st.markdown("---")
st.caption("Developed for sustainability analytics and eco-innovation 🌎")

