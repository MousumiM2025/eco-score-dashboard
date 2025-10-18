import streamlit as st
import pandas as pd
import plotly.express as px

# Load CSV
df = pd.read_csv("ecoscore_data_extended.csv")

# ---- Sidebar Filters ----
st.sidebar.header("🔍 Filter Products")
min_score, max_score = st.sidebar.slider(
    "Select EcoScore Range:", 0, 100, (40, 90)
)
min_price, max_price = st.sidebar.slider(
    "Select Price Range (USD):", 0, 100, (5, 50)
)

# Filtered data
df_selected = df[
    (df["EcoScore"] >= min_score) &
    (df["EcoScore"] <= max_score) &
    (df["Price_USD"] >= min_price) &
    (df["Price_USD"] <= max_price)
]

# ---- App Layout ----
st.set_page_config(page_title="EcoScore.AI Dashboard", layout="wide")

# Header with logo
col1, col2 = st.columns([0.2, 1])
with col1:
    st.image("logo.png", width=100)
with col2:
    st.markdown(
        "<h1 style='color:#2E8B57;'>EcoScore.AI — Sustainable Product Insights</h1>",
        unsafe_allow_html=True,
    )

st.write("Compare sustainability, pricing, and carbon impact across personal care and cosmetic products.")

# ---- Data Display ----
st.subheader("🌱 Selected Product Insights")

st.dataframe(
    df_selected[
        ["Product", "Category", "Price_USD", "EcoScore", "Carbon_Intensity_gCO2e", "Packaging"]
    ].style.format({"Price_USD": "${:,.2f}", "Carbon_Intensity_gCO2e": "{:.1f} gCO₂e"}),
    use_container_width=True
)

# ---- Charts ----
st.subheader("📊 Quick Insights (Selected Products)")

col3, col4 = st.columns(2)

with col3:
    fig1 = px.scatter(
        df_selected,
        x="Price_USD",
        y="EcoScore",
        color="Category",
        hover_name="Product",
        size="EcoScore",
        title="EcoScore vs. Price (Sustainability vs Cost)"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col4:
    fig2 = px.scatter(
        df_selected,
        x="EcoScore",
        y="Carbon_Intensity_gCO2e",
        color="Category",
        hover_name="Product",
        size="EcoScore",
        title="EcoScore vs. Carbon Intensity (Sustainability vs Emissions)"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---- Dynamic Explanation ----
avg_carbon = df_selected["Carbon_Intensity_gCO2e"].mean()
high_carbon = df_selected[df_selected["Carbon_Intensity_gCO2e"] > avg_carbon]

if not high_carbon.empty:
    st.info(
        f"⚠️ Some selected products show higher carbon intensity than average ({avg_carbon:.1f} gCO₂e). "
        "This may be due to energy-intensive production, heavy packaging, or long-distance transportation."
    )

# ---- Footer ----
st.markdown(
    """
    <hr style="border:1px solid #2E8B57;">
    <p style='text-align:center; color:gray; font-size:14px;'>
    © 2025 EcoScore.AI — All rights reserved
    </p>
    """,
    unsafe_allow_html=True
)

