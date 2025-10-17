import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import base64

# ==============================
# Page Configuration
# ==============================
st.set_page_config(
    page_title="EcoScore.AI Dashboard",
    page_icon="🌿",
    layout="wide"
)

# ==============================
# Utility - Background Image
# ==============================
def add_bg_from_local(image_file):
    with open(image_file, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    page_bg_img = f"""
    <style>
    .stApp {{
        background-color: #f6fdf7;
        background-image: url("data:image/jpg;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Set background (uploaded butterfly image)
add_bg_from_local("1377525_1658200317780476_8339243329544761042_n.jpg")

# ==============================
# Load Dataset
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("ecoscore_data_2023.csv")
    return df

data = load_data()

# ==============================
# Header Section
# ==============================
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/70/Leaf_icon_green.svg",
             width=120)
with col2:
    st.markdown(
        "<h1 style='color:#0c6b2f; font-size:46px; font-weight:700; text-shadow:1px 1px #a3d3a2;'>EcoScore.AI 🌍</h1>",
        unsafe_allow_html=True)
    st.markdown("<h4 style='color:#155c2e;'>Compare sustainability, price, and impact across everyday products.</h4>",
                unsafe_allow_html=True)

st.markdown("---")

# ==============================
# Product Selection
# ==============================
st.sidebar.header("🔍 Filter Options")

category_list = sorted(data["Category"].unique())
selected_category = st.sidebar.selectbox("Select Product Category", category_list)

filtered_products = data[data["Category"] == selected_category]["Product"].unique()
selected_products = st.sidebar.multiselect("Select Products to Compare", filtered_products)

# ==============================
# Display Results
# ==============================
if selected_products:
    df_selected = data[data["Product"].isin(selected_products)]

    st.markdown(f"<h3 style='color:#0b4b26;'>Quick Insights ({selected_category})</h3>", unsafe_allow_html=True)

    # Display product comparison table
    st.dataframe(
        df_selected[["Product", "Price_USD", "EcoScore", "Carbon_Intensity_gCO2e", "Packaging", "Main_Ingredients"]],
        use_container_width=True,
        hide_index=True
    )

    # Plot EcoScore vs Price
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(df_selected["Price_USD"], df_selected["EcoScore"], s=120, c="#2a9d54", alpha=0.7)
    for i, row in df_selected.iterrows():
        ax.text(row["Price_USD"], row["EcoScore"], row["Product"], fontsize=8, ha='right')
    ax.set_xlabel("Price (USD)")
    ax.set_ylabel("EcoScore")
    ax.set_title(f"EcoScore vs Price for {selected_category}")
    ax.grid(True, linestyle='--', alpha=0.4)
    st.pyplot(fig)

else:
    st.info("👈 Select a category and products to compare from the sidebar.")

# ==============================
# Footer
# ==============================
st.markdown("""
    <hr style='border:1px solid #9bcc9b;'>
    <div style='text-align:center; color:#0b4b26; font-size:14px;'>
        © 2025 EcoScore.AI — All rights reserved
    </div>
""", unsafe_allow_html=True)
