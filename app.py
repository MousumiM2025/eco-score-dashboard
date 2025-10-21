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

df = load_data()

# -------------------------------
# COUNTRY EMISSION FACTORS
# -------------------------------
country_factors = {
    "USA": 1.00,
    "Germany": 0.85,
    "France": 0.75,
    "China": 1.25,
    "India": 1.15,
    "Brazil": 0.90,
    "Japan": 0.80,
}

# -------------------------------
# USER SELECTIONS
# -------------------------------
categories = sorted(df["Category"].dropna().unique())
selected_category = st.selectbox("Select Product Category", categories)

product_list = df[df["Category"] == selected_category]["Product"].dropna().unique()
selected_products = st.multiselect(
    "Select Products to Compare",
    product_list,
    default=product_list[:2] if len(product_list) > 1 else product_list
)

selected_country = st.selectbox("🌎 Select Country of Manufacture", list(country_factors.keys()), index=0)

st.markdown("---")

# -------------------------------
# FILTER & ADJUST DATA
# -------------------------------
df_selected = df[df["Product"].isin(selected_products)].copy()

if df_selected.empty:
    st.warning("Please select one or more products to compare.")
    st.stop()

# Apply country emission multiplier
factor = country_factors[selected_country]
df_selected["Adjusted_Carbon"] = df_selected["Carbon_Intensity_gCO2e"] * factor

# -------------------------------
# WHAT-IF SIMULATOR
# -------------------------------
st.markdown("### 🔄 What-if Scenario Simulator")
col1, col2 = st.columns(2)

packaging_change = col1.selectbox(
    "Change Packaging Type",
    ["No Change", "Recycled Cardboard", "Aluminum Refill", "Glass Reusable", "Compostable Pouch"],
)

eco_improvement = col2.slider("Improve Ingredient Sustainability (%)", 0, 50, 0)

# Recalculate EcoScore
df_selected["Simulated_EcoScore"] = df_selected["EcoScore"]

if packaging_change != "No Change":
    df_selected["Simulated_EcoScore"] += 5  # small boost
if eco_improvement > 0:
    df_selected["Simulated_EcoScore"] += eco_improvement * 0.4  # scaled improvement
df_selected["Simulated_EcoScore"] = df_selected["Simulated_EcoScore"].clip(0, 100)

st.markdown("---")

# -------------------------------
# QUICK INSIGHTS
# -------------------------------
st.markdown("### ⚡ Quick Insights (Simulated Results)")
avg_price = df_selected["Price_USD"].mean()
avg_eco = df_selected["Simulated_EcoScore"].mean()
avg_carbon = df_selected["Adjusted_Carbon"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Average Price", f"${avg_price:,.2f}")
col2.metric("Avg. Simulated EcoScore", f"{avg_eco:.1f} / 100")
col3.metric("Avg. Adjusted Carbon", f"{avg_carbon:.1f} gCO₂e")

st.markdown("---")

# -------------------------------
# SCATTER PLOTS
# -------------------------------
tab1, tab2 = st.tabs(["EcoScore vs Adjusted Carbon", "EcoScore vs Price"])

with tab1:
    fig1 = px.scatter(
        df_selected,
        x="Adjusted_Carbon",
        y="Simulated_EcoScore",
        color="Product",
        size="Simulated_EcoScore",
        hover_data=["Product", "Category", "Price_USD", "Packaging", "Recyclability_Score", "Country"],
        title=f"EcoScore vs Adjusted Carbon Intensity ({selected_country} Factor {factor}×)",
    )
    fig1.update_layout(template="plotly_white", height=500)
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = px.scatter(
        df_selected,
        x="Price_USD",
        y="Simulated_EcoScore",
        color="Product",
        size="Simulated_EcoScore",
        hover_data=["Product", "Category", "Price_USD", "Packaging", "Recyclability_Score"],
        title="EcoScore vs Price (Sustainability vs Cost)",
    )
    fig2.update_layout(template="plotly_white", height=500)
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# TABLE
# -------------------------------
st.markdown("### 🧴 Product Details After Simulation")
cols = [
    "Product", "Category", "Price_USD", "EcoScore", "Simulated_EcoScore",
    "Carbon_Intensity_gCO2e", "Adjusted_Carbon", "Packaging", "Recyclability_Score", "Main_Ingredients"
]
cols_available = [c for c in cols if c in df_selected.columns]

st.dataframe(
    df_selected[cols_available].style.format({
        "Price_USD": "${:,.2f}",
        "Carbon_Intensity_gCO2e": "{:.1f}",
        "Adjusted_Carbon": "{:.1f}",
        "EcoScore": "{:.0f}",
        "Simulated_EcoScore": "{:.0f}"
    }),
    use_container_width=True
)

# -------------------------------
# SCORING METHODOLOGY
# -------------------------------
st.markdown("---")
with st.expander("📘 How EcoScore is Measured"):
    st.markdown("""
    **EcoScore (0–100)** blends environmental performance across four weighted factors:

    | Component | Weight | Description |
    |------------|---------|-------------|
    | ♻️ Ingredient safety | 40% | Toxicity, biodegradability |
    | 🌍 Carbon intensity | 30% | Lifecycle CO₂e adjusted by country |
    | 📦 Packaging | 20% | Recyclability, reusability, material impact |
    | 💰 Affordability | 10% | Price efficiency |

    🧩 The "What-if" simulator lets you experiment with packaging and ingredient improvements.
    """)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("© 2025 EcoScore.AI — Sustainability Insight Prototype")


