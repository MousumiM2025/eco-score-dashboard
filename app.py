import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="EcoScore Dashboard", page_icon="🌿", layout="wide")

st.markdown(
    """
    <h1 style='text-align:center; color:#2E8B57;'>🌿 EcoScore Dashboard</h1>
    <p style='text-align:center;'>Compare sustainability, pricing, and carbon impact across consumer products.</p>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ecoscore_data_extended_v2.csv")
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Could not find ecoscore_data_extended_v2.csv. Please upload or place it in the app folder.")
    st.stop()

# -------------------------------
# VERIFY KEY COLUMNS
# -------------------------------
required_cols = ["Product", "Category", "Price_USD", "EcoScore", "Carbon_Intensity_gCO2e"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# -------------------------------
# CATEGORY AND PRODUCT SELECTION
# -------------------------------
categories = sorted(df["Category"].dropna().unique())
selected_category = st.selectbox("Select Product Category", categories)

product_list = df[df["Category"] == selected_category]["Product"].dropna().unique()
selected_products = st.multiselect(
    "Select Products to Compare",
    product_list,
    default=product_list[:2] if len(product_list) > 1 else product_list
)

df_selected = df[df["Product"].isin(selected_products)]

if df_selected.empty:
    st.warning("Please select one or more products to compare.")
    st.stop()

# -------------------------------
# QUICK INSIGHTS SECTION
# -------------------------------
st.markdown("### ⚡ Quick Insights (Selected Products)")
avg_price = df_selected["Price_USD"].mean()
avg_ecoscore = df_selected["EcoScore"].mean()
avg_carbon = df_selected["Carbon_Intensity_gCO2e"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Average Price", f"${avg_price:,.2f}")
col2.metric("Average EcoScore", f"{avg_ecoscore:.1f} / 100")
col3.metric("Average Carbon Intensity", f"{avg_carbon:.1f} gCO₂e")

st.markdown("---")

# -------------------------------
# COMPARISON SCATTER PLOTS
# -------------------------------
st.markdown("### 📈 Visual Comparison")

tab1, tab2 = st.tabs(["EcoScore vs Carbon Intensity", "EcoScore vs Price"])

with tab1:
    fig1 = px.scatter(
        df_selected,
        x="Carbon_Intensity_gCO2e",
        y="EcoScore",
        color="Product",
        size="EcoScore",
        hover_data=["Product", "Category", "Price_USD", "Packaging", "Recyclability_Score", "Country"],
        title="EcoScore vs Carbon Intensity (Sustainability vs Emissions)",
    )
    fig1.update_layout(template="plotly_white", height=500)
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = px.scatter(
        df_selected,
        x="Price_USD",
        y="EcoScore",
        color="Product",
        size="EcoScore",
        hover_data=["Product", "Category", "Price_USD", "Packaging", "Recyclability_Score", "Country"],
        title="EcoScore vs Price (Sustainability vs Cost)",
    )
    fig2.update_layout(template="plotly_white", height=500)
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# PRODUCT DETAILS TABLE
# -------------------------------
st.markdown("### 🧴 Selected Product Details")

detail_cols = [
    "Product",
    "Category",
    "Price_USD",
    "EcoScore",
    "Carbon_Intensity_gCO2e",
    "Packaging",
    "Recyclability_Score",
    "Main_Ingredients",
]
available_cols = [c for c in detail_cols if c in df_selected.columns]

st.dataframe(
    df_selected[available_cols].style.format({
        "Price_USD": "${:,.2f}",
        "Carbon_Intensity_gCO2e": "{:.1f} gCO₂e",
        "EcoScore": "{:.0f}"
    }),
    use_container_width=True
)

# -------------------------------
# SCORING METHODOLOGY SECTION
# -------------------------------
st.markdown("---")
with st.expander("📘 How EcoScore is Measured"):
    st.markdown("""
    **EcoScore (0–100)** combines multiple sustainability factors into a single index.  
    The weights below show how each aspect contributes to the total score:

    | Component | Weight | Description |
    |------------|---------|-------------|
    | 🌿 **Ingredient safety & biodegradability** | 40% | Based on toxicity and renewable source indicators |
    | 🌍 **Carbon intensity (lifecycle CO₂e)** | 30% | Estimated cradle-to-grave emissions per unit |
    | 📦 **Packaging sustainability & recyclability** | 20% | Material composition and end-of-life recyclability |
    | 💰 **Affordability / Accessibility** | 10% | Price normalized to category baseline |

    🧠 *This dashboard uses a synthetic dataset for demonstration.  
    Future versions will integrate verified LCA, supplier, and ingredient databases.*
    """)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("© 2025 EcoScore.AI — Prototype version for sustainability analytics.")


