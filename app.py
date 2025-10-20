#--Code Works
import streamlit as st
import pandas as pd
import altair as alt

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("ecoscore_data_2023.csv")
    return df

df = load_data()

# --- Title and Intro ---
st.title("🌍 EcoScore Comparison Dashboard")
st.markdown("""
Compare **price**, **eco-score**, and **carbon intensity** across consumer products.  
Use the dropdowns below to explore categories and items.
""")

# --- Category and Product Selection ---
categories = sorted(df["Category"].unique())
selected_category = st.selectbox("Select Product Category", categories)

products = df[df["Category"] == selected_category]["Product"].unique()
selected_products = st.multiselect(
    "Select Products to Compare", 
    products, 
    default=[products[0]] if len(products) > 0 else None
)

# --- Filter data ---
filtered_df = df[df["Product"].isin(selected_products)]

if not filtered_df.empty:
    st.subheader(f"📊 Comparison in {selected_category}")

    # --- Display Table ---
    st.dataframe(filtered_df[["Product", "Brand", "Price_USD", "EcoScore", "Carbon_Intensity_gCO2eq", "Main_Ingredients", "Packaging_Type"]])

    # --- Chart: Price vs EcoScore ---
    st.subheader("💵 Price vs ♻️ EcoScore")
    chart = (
        alt.Chart(filtered_df)
        .mark_circle(size=100)
        .encode(
            x="Price_USD",
            y="EcoScore",
            color="Product",
            tooltip=["Product", "Price_USD", "EcoScore", "Carbon_Intensity_gCO2eq"]
        )
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

    # --- Chart: EcoScore vs Carbon Intensity ---
    st.subheader("🌱 EcoScore vs 🏭 Carbon Intensity")
    chart2 = (
        alt.Chart(filtered_df)
        .mark_circle(size=100)
        .encode(
            x="EcoScore",
            y="Carbon_Intensity_gCO2eq",
            color="Product",
            tooltip=["Product", "EcoScore", "Carbon_Intensity_gCO2eq"]
        )
        .interactive()
    )
    st.altair_chart(chart2, use_container_width=True)

else:
    st.warning("Please select at least one product to view comparison.")

# --- Footer ---
st.markdown("---")
st.markdown("🔗 *EcoScore Dashboard Prototype – 2023 Baseline Data*")




