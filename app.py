import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------
# PAGE CONFIG & LOGO
# --------------------------
st.set_page_config(page_title="EcoScore Dashboard", layout="wide")

st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Leaf_icon_02.svg/512px-Leaf_icon_02.svg.png",
    width=80,
)
st.title("🌱 EcoScore Dashboard — Extended Version")
st.markdown("### An interactive tool to explore sustainability metrics for products")

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

# Display detected columns (debug)
with st.expander("🔍 Detected column mapping"):
    st.write({
        "Product": col_product,
        "Category": col_category,
        "Price": col_price,
        "EcoScore": col_ecoscore,
        "Carbon Intensity": col_carbon,
        "Packaging": col_packaging,
    })

# --------------------------
# SIDEBAR FILTERS
# --------------------------
st.sidebar.header("🎚️ Filters")

if col_price:
    min_price, max_price = df[col_price].min(), df[col_price].max()
    price_range = st.sidebar.slider(
        "Select Price Range ($)", float(min_price), float(max_price), (float(min_price), float(max_price))
    )
else:
    price_range = None

if col_ecoscore:
    min_score, max_score = df[col_ecoscore].min(), df[col_ecoscore].max()
    score_range = st.sidebar.slider(
        "Select EcoScore Range", float(min_score), float(max_score), (float(min_score), float(max_score))
    )
else:
    score_range = None

df_selected = df.copy()
if price_range and col_price:
    df_selected = df_selected[df_selected[col_price].between(price_range[0], price_range[1])]
if score_range and col_ecoscore:
    df_selected = df_selected[df_selected[col_ecoscore].between(score_range[0], score_range[1])]

# --------------------------
# MAIN DATA DISPLAY
# --------------------------
st.markdown("### 📊 Filtered Data")
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
    st.warning("⚠️ Some expected columns were not found. Check column names above.")

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
            title="EcoScore vs Price",
            hover_data=[col_product],
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
            title="EcoScore vs Carbon Intensity",
            hover_data=[col_product],
            trendline="ols",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("EcoScore or Carbon Intensity column not found.")

# --------------------------
# EXPLANATION SECTION
# --------------------------
st.markdown("""
---
### ♻️ Understanding Carbon Intensity
Products with **higher carbon intensity** often have:
- 🌍 Longer or more complex supply chains  
- ⚙️ Energy-intensive manufacturing steps  
- 🧴 Non-recyclable or fossil-based packaging  
- 💰 Lower EcoScore (more emissions per function)

Improving packaging, sourcing cleaner materials, or shifting to renewable energy can
**raise EcoScore and reduce overall carbon footprint**.
""")

# --------------------------
# FOOTER
# --------------------------
st.markdown("---")
st.caption("Developed for sustainability analytics and eco-innovation 🌎")


