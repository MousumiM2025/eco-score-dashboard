import streamlit as st
import pandas as pd
import plotly.express as px

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
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/7/70/Leaf_icon_green.svg",
        width=120
    )
with col2:
    st.markdown(
        "<h1 style='color:#0c6b2f; font-size:42px; font-weight:700;'>EcoScore.AI 🌍</h1>",
        unsafe_allow_html=True
    )
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

    # ---- Safe Column Display ----
    available_cols = df_selected.columns.tolist()
    desired_cols = [
        "Product",
        "Price_USD",
        "EcoScore",
        "Carbon_Intensity_gCO2e",
        "Packaging",
        "Main_Ingredients"
    ]
    show_cols = [col for col in desired_cols if col in available_cols]

    if show_cols:
        st.dataframe(
            df_selected[show_cols],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ No matching columns found to display.")

    # ==============================
    # Scatter Plots
    # ==============================
    st.markdown("### 💡 Visual Insights")

    col_plot1, col_plot2 = st.columns(2)

    # ---- EcoScore vs Price ----
    if "EcoScore" in available_cols and "Price_USD" in available_cols:
        with col_plot1:
            fig1 = px.scatter(
                df_selected,
                x="Price_USD",
                y="EcoScore",
                color="Product",
                size="EcoScore",
                hover_data=["Packaging", "Carbon_Intensity_gCO2e"],
                title="EcoScore vs. Price (Sustainability vs Cost)"
            )
            fig1.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
            fig1.update_layout(
                title_font=dict(size=16, color="#0b4b26"),
                paper_bgcolor="white",
                plot_bgcolor="#eef6ef",
                font=dict(color="#0b4b26"),
                legend_title_text="Products"
            )
            st.plotly_chart(fig1, use_container_width=True)

    # ---- EcoScore vs Carbon Intensity ----
    if "EcoScore" in available_cols and "Carbon_Intensity_gCO2e" in available_cols:
        with col_plot2:
            fig2 = px.scatter(
                df_selected,
                x="Carbon_Intensity_gCO2e",
                y="EcoScore",
                color="Product",
                size="EcoScore",
                hover_data=["Packaging", "Price_USD"],
                title="EcoScore vs. Carbon Intensity (Sustainability vs Emissions)"
            )
            fig2.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
            fig2.update_layout(
                title_font=dict(size=16, color="#0b4b26"),
                paper_bgcolor="white",
                plot_bgcolor="#eef6ef",
                font=dict(color="#0b4b26"),
                legend_title_text="Products"
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ==============================
    # Score Explanation
    # ==============================
    st.markdown("---")
    st.markdown(
        """
        ### 🌱 How EcoScore Works
        - **EcoScore (0–100)**: Composite rating based on product sustainability — higher means better.
        - **Carbon Intensity (gCO₂e)**: Estimated emissions per functional unit; lower is greener.
        - **Packaging Impact**: Evaluates recyclability and material type (plastic, glass, paper, refillable).
        - **Price (USD)**: Typical retail price, used to understand cost-to-sustainability balance.
        - **Main Ingredients**: Key formulation components used for health and environmental safety screening.
        """,
        unsafe_allow_html=True
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

