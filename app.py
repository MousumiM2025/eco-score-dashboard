import streamlit as st
import pandas as pd

# ==============================
# Page Configuration
# ==============================
st.set_page_config(
    page_title="EcoScore.AI Dashboard",
    page_icon="🌿",
    layout="wide"
)

# ==============================
# Load Dataset
# ==============================
@st.cache_data
def load_data():
    return pd.read_csv("ecoscore_data_2023.csv")

data = load_data()

# ==============================
# Header
# ==============================
col1, col2 = st.columns([1, 5])
with col1:
    # Simple leaf logo placeholder
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/70/Leaf_icon_green.svg",
             width=100)
with col2:
    st.markdown(
        "<h1 style='color:#0c6b2f; font-size:42px; font-weight:700;'>EcoScore.AI 🌍</h1>",
        unsafe_allow_html=True)
    st.markdown(
        "<h5 style='color:#2b7a3e;'>Compare sustainability, price, and carbon impact across everyday products.</h5>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ==============================
# Sidebar Filters
# ==============================
st.sidebar.header("🔍 Filter Options")

categories = sorted(data["Category"].unique())
selected_category = st.sidebar.selectbox("Select Product Category", categories)

products = sorted(data[data["Category"] == selected_category]["Product"].unique())
selected_products = st.sidebar.multiselect("Select Products to Compare", products)

# ==============================
# Display Section
# ==============================
if selected_products:
    df_selected = data[data["Product"].isin(selected_products)]

    st.markdown(
        f"<h3 style='color:#0b4b26;'>Quick Insights — {selected_category}</h3>",
        unsafe_allow_html=True
    )

    # Display main table
    st.dataframe(
        df_selected[
            ["Product", "Price_USD", "EcoScore", "Carbon_Intensity_gCO2e", "Packaging", "Main_Ingredients"]
        ],
        use_container_width=True,
        hide_index=True
    )

    # Streamlit built-in chart (no matplotlib dependency)
    st.markdown("### 💡 EcoScore vs Price")
    st.bar_chart(
        df_selected.set_index("Product")[["EcoScore", "Price_USD"]],
        use_container_width=True
    )

else:
    st.info("👈 Use the sidebar to select a category and products for comparison.")

# ==============================
# Footer
# ==============================
st.markdown("""
    <hr style='border:1px solid #9bcc9b;'>
    <div style='text-align:center; color:#0b4b26; font-size:14px;'>
        © 2025 EcoScore.AI — All rights reserved
    </div>
""", unsafe_allow_html=True)

