import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------
# App Configuration
# ------------------------------------------------
st.set_page_config(page_title="EcoScore.AI", page_icon="🌿", layout="wide")

# ------------------------------------------------
# Load Data
# ------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ecoscore_data_extended.csv")
    return df

df = load_data()

# ------------------------------------------------
# Header
# ------------------------------------------------
col1, col2 = st.columns([1, 5])
with col1:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/7/70/Leaf_icon_green.svg",
        width=100,
    )
with col2:
    st.markdown(
        "<h1 style='color:#0c6b2f; font-size:38px; font-weight:700;'>EcoScore.AI Dashboard</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size:18px; color:#2b7a3e;'>Compare sustainability, price, and carbon intensity across daily-use products.</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ------------------------------------------------
# Dropdowns for Category & Product Selection
# ------------------------------------------------
categories = df["Category"].unique().tolist()
selected_category = st.selectbox("Select a Category", sorted(categories))

filtered_df = df[df["Category"] == selected_category]
products = filtered_df["Product"].unique().tolist()
selected_products = st.multiselect("Select one or more Products", sorted(products))

# ------------------------------------------------
# Display Selected Product Info
# ------------------------------------------------
if selected_products:
    df_selected = filtered_df[filtered_df["Product"].isin(selected_products)]

    # Ensure numeric types for plotting
    for col in ["Price_USD", "EcoScore", "Carbon_Intensity_gCO2e"]:
        if col in df_selected.columns:
            df_selected[col] = pd.to_numeric(df_selected[col], errors="coerce")

    st.subheader("Product Comparison Table")
    st.dataframe(
        df_selected[
            [
                "Product",
                "Price_USD",
                "EcoScore",
                "Carbon_Intensity_gCO2e",
                "Packaging",
                "Main_Ingredients",
            ]
        ].style.format({"Price_USD": "${:,.2f}", "Carbon_Intensity_gCO2e": "{:.1f} gCO₂e"}),
        use_container_width=True,
    )

    # ------------------------------------------------
    # Scatter Plot 1: EcoScore vs Price
    # ------------------------------------------------
    st.markdown("### 📊 EcoScore vs Price (Sustainability vs Cost)")
    fig1 = px.scatter(
        df_selected,
        x="Price_USD",
        y="EcoScore",
        color="Product",
        size="EcoScore",
        hover_data=["Category"],
        title="EcoScore vs Price",
    )
    fig1.update_layout(title_x=0.5, template="plotly_white", height=400)
    st.plotly_chart(fig1, use_container_width=True)

    # ------------------------------------------------
    # Scatter Plot 2: EcoScore vs Carbon Intensity
    # ------------------------------------------------
    st.markdown("### 🌎 EcoScore vs Carbon Intensity")
    fig2 = px.scatter(
        df_selected,
        x="Carbon_Intensity_gCO2e",
        y="EcoScore",
        color="Product",
        size="Price_USD",
        hover_data=["Category"],
        title="EcoScore vs Carbon Intensity",
    )
    fig2.update_layout(title_x=0.5, template="plotly_white", height=400)
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("👈 Please select a category and one or more products to compare.")

# ------------------------------------------------
# EcoScore Explanation
# ------------------------------------------------
st.markdown("---")
st.markdown(
    """
    ### ♻️ About EcoScore
    EcoScore combines multiple sustainability indicators:
    - **Environmental footprint**: Life cycle carbon emissions and resource usage  
    - **Packaging impact**: Material recyclability and volume  
    - **Ingredient safety**: Environmental and health considerations  
    - **Social transparency**: Ethical sourcing and corporate practices  

    A higher **EcoScore (closer to 100)** indicates a more environmentally friendly and transparent product.
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------
# Footer
# ------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; color:#2b7a3e; font-size:14px;'>
    © 2025 EcoScore.AI — All rights reserved
    </div>
    """,
    unsafe_allow_html=True,
)
