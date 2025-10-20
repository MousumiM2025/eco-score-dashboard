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

    # --- Quick Insights ---
    avg_price = filtered_df["Price_USD"].mean()
    avg_eco = filtered_df["EcoScore"].mean()
    avg_carbon = filtered_df["Carbon_Intensity_gCO2eq"].mean()

    st.markdown(f"""
    ### ⚡ Quick Insights (Selected Products)
    - **Average Price:** ${avg_price:,.2f}
    - **Average EcoScore:** {avg_eco:.1f} / 100  
    - **Average Carbon Intensity:** {avg_carbon:.1f} gCO₂e
    """)
    st.markdown("---")

    # --- Display Table ---
    st.subheader("🧴 Product Details")
    st.dataframe(
        filtered_df[
            ["Product", "Brand", "Price_USD", "EcoScore", "Carbon_Intensity_gCO2eq", "Main_Ingredients", "Packaging_Type"]
        ],
        use_container_width=True,
    )

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

    # --- Scoring Methodology Section ---
    with st.expander("📘 How EcoScore is Measured"):
        st.markdown("""
        **EcoScore (0–100)** combines environmental impact factors into a single number.  
        The model used here is a simplified prototype:

        | Component | Weight | Description |
        |------------|---------|-------------|
        | ♻️ **Ingredient safety & biodegradability** | 40% | Based on non-toxic, renewable ingredients |
        | 🌍 **Carbon intensity** | 30% | Lifecycle CO₂e emissions per product |
        | 📦 **Packaging sustainability** | 20% | Material type and recyclability |
        | 💰 **Affordability / Price efficiency** | 10% | Normalized cost vs category baseline |

        👉 *This is an illustrative scoring system using baseline 2023 data.  
        Future versions will integrate verified LCA data and supplier disclosures.*
        """)

else:
    st.warning("Please select at least one product to view comparison.")

# --- Footer ---
st.markdown("---")
st.markdown("🔗 *EcoScore Dashboard Prototype – 2023 Baseline Data*")
st.caption("© 2025 EcoScore.AI — All rights reserved")

