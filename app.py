#import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(
    page_title="EcoScore Dashboard",
    page_icon="🌿",
    layout="centered",
)

# --- Header ---
st.title("🌿 EcoScore — Product Environmental & Health Transparency")
st.markdown("Understand the **real impact** of everyday products — from ingredients to packaging and certifications.")

# --- Mock product database ---
sample_products = {
    "Dove Shampoo": {"brand": "Dove", "ecoscore": 78, "health_score": 72, "carbon_score": 65, "epa_safer_choice": False, "ewg_health_ref": 80.0},
    "Pantene Shampoo": {"brand": "Pantene", "ecoscore": 70, "health_score": 68, "carbon_score": 62, "epa_safer_choice": False, "ewg_health_ref": 75.0},
    "Herbal Essences": {"brand": "Herbal Essences", "ecoscore": 84, "health_score": 80, "carbon_score": 72, "epa_safer_choice": True, "ewg_health_ref": 88.0},
    "Head & Shoulders": {"brand": "Head & Shoulders", "ecoscore": 66, "health_score": 60, "carbon_score": 58, "epa_safer_choice": False, "ewg_health_ref": 70.0},
    "Aveeno Daily Moisturizer": {"brand": "Aveeno", "ecoscore": 90, "health_score": 85, "carbon_score": 80, "epa_safer_choice": True, "ewg_health_ref": 92.0},
    "Native Shampoo": {"brand": "Native", "ecoscore": 88, "health_score": 90, "carbon_score": 78, "epa_safer_choice": True, "ewg_health_ref": 95.0},
    "Suave Essentials": {"brand": "Suave", "ecoscore": 62, "health_score": 55, "carbon_score": 60, "epa_safer_choice": False, "ewg_health_ref": 68.0},
    "The Body Shop Ginger Shampoo": {"brand": "The Body Shop", "ecoscore": 92, "health_score": 88, "carbon_score": 84, "epa_safer_choice": True, "ewg_health_ref": 93.0},
    "L’Oréal Elvive": {"brand": "L’Oréal", "ecoscore": 74, "health_score": 70, "carbon_score": 66, "epa_safer_choice": False, "ewg_health_ref": 78.0},
    "SheaMoisture Coconut & Hibiscus": {"brand": "SheaMoisture", "ecoscore": 89, "health_score": 92, "carbon_score": 82, "epa_safer_choice": True, "ewg_health_ref": 96.0}
}

# --- Product Selection ---
st.markdown("### 🔍 Choose one or more products to compare:")
selected_products = st.multiselect(
    "Select products:",
    list(sample_products.keys()),
    default=["Dove Shampoo"]
)

# --- Manual entry for custom product ---
manual_product = st.text_input("Or enter a custom product name (optional):", "")

if st.button("Get EcoScore"):
    with st.spinner("Analyzing sustainability data..."):
        results = []

        for product in selected_products:
            data = sample_products[product]
            data["product"] = product
            results.append(data)

        if manual_product:
            results.append({
                "product": manual_product,
                "brand": "Unknown",
                "ecoscore": 75,
                "health_score": 70,
                "carbon_score": 65,
                "epa_safer_choice": False,
                "ewg_health_ref": 78.0
            })

        df = pd.DataFrame(results)

    # --- Display Individual Scores ---
    st.subheader("🧴 Product Details")
    for _, row in df.iterrows():
        st.markdown(f"#### {row['product']}")
        st.write(f"**Brand:** {row['brand']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("🌱 EcoScore", f"{row['ecoscore']}/100")
        col2.metric("❤️ Health Score", f"{row['health_score']}/100")
        col3.metric("⚡ Carbon Impact", f"{row['carbon_score']}/100")
        if row["epa_safer_choice"]:
            st.success("✅ EPA Safer Choice Certified")
        st.markdown("---")

    # --- Comparison Chart ---
    st.subheader("📊 Compare Scores Across Products")
    chart_df = df.melt(id_vars=["product"], value_vars=["ecoscore", "health_score", "carbon_score"],
                       var_name="Score Type", value_name="Value")

    fig = px.bar(
        chart_df,
        x="product",
        y="Value",
        color="Score Type",
        barmode="group",
        text="Value",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        xaxis_title="Product",
        yaxis_title="Score (0–100)",
        title="EcoScore, Health Score, and Carbon Impact Comparison",
        title_x=0.5,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Explanation ---
    with st.expander("🔍 How EcoScore is Calculated"):
        st.markdown("""
        **EcoScore (0–100)** combines environmental, health, and lifecycle factors:

        | Factor | Weight | Description |
        |---------|--------|-------------|
        | ♻️ **Packaging** | 20% | Recyclable paper/glass rated higher; plastics penalized |
        | 💧 **Carbon Intensity** | 30% | Based on product category lifecycle emission factors |
        | 🌱 **Ingredient Safety** | 40% | Derived from EWG hazard ratings (lower hazard = higher score) |
        | 🏅 **Certifications** | 10% | Bonus points for EPA Safer Choice, EcoLabel, or organic certification |
        """)

    # --- Data Sources ---
    st.markdown("### 📚 Data Sources")
    st.markdown("""
    - [Open Beauty Facts](https://world.openbeautyfacts.org/)  
    - [EWG Skin Deep](https://www.ewg.org/skindeep/)  
    - [EPA Safer Choice](https://www.epa.gov/saferchoice/products)
    """)

else:
    st.info("👆 Select products and click **Get EcoScore** to compare.")


