# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# Helper: flexible column finder
# ----------------------------
def find_col(df, candidates):
    """Return the first column name in df.columns that matches any candidate (case-insensitive)."""
    cols = list(df.columns)
    low_to_orig = {c.strip().lower(): c for c in cols}
    for cand in candidates:
        key = cand.strip().lower()
        if key in low_to_orig:
            return low_to_orig[key]
    # fallback: try substrings
    for cand in candidates:
        cand_low = cand.strip().lower()
        for c in cols:
            if cand_low in c.strip().lower():
                return c
    return None

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="EcoScore.AI", page_icon="🌿", layout="wide")

# ----------------------------
# Load data
# ----------------------------
@st.cache_data
def load_data(path="ecoscore_data_extended.csv"):
    try:
        df = pd.read_csv(path)
        # strip whitespace from column names
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error loading CSV '{path}': {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# ----------------------------
# Detect useful columns (flexible)
# ----------------------------
COL_CATEGORY = find_col(df, ["Category"])
COL_PRODUCT = find_col(df, ["Product", "Product Name", "product"])
COL_BRAND = find_col(df, ["Brand"])
COL_PRICE = find_col(df, ["Price_USD", "Price (USD)", "Price", "price_usd"])
COL_ECOSCORE = find_col(df, ["EcoScore", "ecoscore", "Eco Score"])
COL_CARBON = find_col(df, ["Carbon_Intensity_gCO2eq", "Carbon_Intensity_kgCO2e", "Carbon_Intensity", "carbon_intensity"])
COL_PACK = find_col(df, ["Packaging", "Packaging_Type", "Packaging Type"])
COL_ING = find_col(df, ["Main_Ingredients", "Main Ingredients", "Ingredients", "ingredients"])

# minimal validation
required = [COL_CATEGORY, COL_PRODUCT]
if not all(required):
    st.error("CSV must have at least 'Category' and 'Product' columns (or similar). Found: " + ", ".join(df.columns))
    st.stop()

# ----------------------------
# Header
# ----------------------------
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/70/Leaf_icon_green.svg", width=110)
with col2:
    st.markdown("<h1 style='color:#0c6b2f; font-size:40px; font-weight:700;'>EcoScore.AI Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#2b7a3e; font-size:16px;'>Compare sustainability, price, and carbon intensity across everyday products (2023 baseline).</p>", unsafe_allow_html=True)

st.markdown("---")

# ----------------------------
# Category & product selectors
# ----------------------------
categories = df[COL_CATEGORY].dropna().unique().tolist()
categories.sort()
selected_category = st.selectbox("Select a Category", categories)

mask_cat = df[COL_CATEGORY] == selected_category
df_cat = df.loc[mask_cat].copy()
products = df_cat[COL_PRODUCT].dropna().unique().tolist()
products.sort()

selected_products = st.multiselect("Select product(s) to compare", products, default=products[:2] if products else [])

# ----------------------------
# Prepare selected dataframe safely
# ----------------------------
if not selected_products:
    st.info("Select one or more products to compare.")
    st.stop()

df_sel = df_cat[df_cat[COL_PRODUCT].isin(selected_products)].copy()
if df_sel.empty:
    st.warning("No rows found for selected products.")
    st.stop()

# normalize numeric columns if present
if COL_PRICE:
    df_sel[COL_PRICE] = pd.to_numeric(df_sel[COL_PRICE], errors="coerce")
if COL_ECOSCORE:
    df_sel[COL_ECOSCORE] = pd.to_numeric(df_sel[COL_ECOSCORE], errors="coerce")
if COL_CARBON:
    df_sel[COL_CARBON] = pd.to_numeric(df_sel[COL_CARBON], errors="coerce")

# ----------------------------
# Build display columns list (only those present)
# ----------------------------
display_cols_candidates = [
    (COL_PRODUCT, "Product"),
    (COL_BRAND, "Brand"),
    (COL_PRICE, "Price (USD)"),
    (COL_ECOSCORE, "EcoScore"),
    (COL_CARBON, "Carbon (gCO₂e)"),
    (COL_PACK, "Packaging"),
    (COL_ING, "Main Ingredients"),
]
display_cols = []
display_col_names = []
for col, nice in display_cols_candidates:
    if col and col in df_sel.columns:
        display_cols.append(col)
        display_col_names.append(nice)

# show table
st.subheader("Product comparison table")
if display_cols:
    display_df = df_sel[display_cols].copy()
    # rename columns for nicer display
    display_df.columns = display_col_names
    # format price / carbon if present
    if "Price (USD)" in display_df.columns:
        display_df["Price (USD)"] = pd.to_numeric(display_df["Price (USD)"], errors="coerce")
    if "Carbon (gCO₂e)" in display_df.columns:
        display_df["Carbon (gCO₂e)"] = pd.to_numeric(display_df["Carbon (gCO₂e)"], errors="coerce")
    st.dataframe(display_df.style.format({
        **({"Price (USD)": "${:,.2f}".format} if "Price (USD)" in display_df.columns else {}),
        **({"Carbon (gCO₂e)": "{:.1f} gCO₂e".format} if "Carbon (gCO₂e)" in display_df.columns else {})
    }), use_container_width=True)
else:
    st.warning("No displayable columns found in the CSV for the comparison table.")

# ----------------------------
# Scatter plots: check prerequisites then plot
# ----------------------------
st.markdown("## Visual Insights")

# Plot 1: EcoScore vs Price
can_plot_price = COL_ECOSCORE and COL_PRICE and (COL_ECOSCORE in df_sel.columns) and (COL_PRICE in df_sel.columns)
if can_plot_price and df_sel[COL_ECOSCORE].notna().any() and df_sel[COL_PRICE].notna().any():
    fig1 = px.scatter(
        df_sel,
        x=COL_PRICE,
        y=COL_ECOSCORE,
        color=COL_PRODUCT,
        size=COL_ECOSCORE,  # size uses ecoscore as visual cue
        hover_data=[c for c in [COL_BRAND, COL_PACK, COL_CARBON] if c in df_sel.columns],
        labels={COL_PRICE: "Price (USD)", COL_ECOSCORE: "EcoScore"},
        title="EcoScore vs Price (Sustainability vs Cost)"
    )
    fig1.update_layout(template="plotly_white", title_x=0.5, height=420)
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("EcoScore vs Price plot unavailable (need numeric 'EcoScore' and 'Price' columns).")

# Plot 2: EcoScore vs Carbon Intensity
can_plot_carbon = COL_ECOSCORE and COL_CARBON and (COL_ECOSCORE in df_sel.columns) and (COL_CARBON in df_sel.columns)
if can_plot_carbon and df_sel[COL_ECOSCORE].notna().any() and df_sel[COL_CARBON].notna().any():
    fig2 = px.scatter(
        df_sel,
        x=COL_CARBON,
        y=COL_ECOSCORE,
        color=COL_PRODUCT,
        size=COL_PRICE if COL_PRICE in df_sel.columns else None,
        hover_data=[c for c in [COL_BRAND, COL_PACK, COL_PRICE] if c in df_sel.columns],
        labels={COL_CARBON: "Carbon Intensity (gCO₂e)", COL_ECOSCORE: "EcoScore"},
        title="EcoScore vs Carbon Intensity (Sustainability vs Emissions)"
    )
    fig2.update_layout(template="plotly_white", title_x=0.5, height=420)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("EcoScore vs Carbon plot unavailable (need numeric 'EcoScore' and carbon intensity columns).")

# ----------------------------
# Score explanation (collapsible)
# ----------------------------
with st.expander("How EcoScore is calculated (click to expand)", expanded=False):
    st.markdown("""
    **EcoScore (0–100)** is a composite indicator that in this prototype combines:
    - **Ingredient safety & biodegradability (40%)** — hazard scoring from public ingredient lists
    - **Carbon intensity (30%)** — estimated lifecycle emissions (g CO₂e per unit)
    - **Packaging sustainability (20%)** — recyclability / material type and refill options
    - **Price fairness / accessibility (10%)** — price normalized to category baseline

    **Notes & data sources:** this is a prototype dataset created for demonstration. Data is synthetic / estimated from multiple public patterns (intended for demonstration only). For production use you should replace with verified LCA and product ingredient data (Open Beauty/Food Facts, EWG, manufacturer disclosures).
    """)

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.markdown("<div style='text-align:center; color:#2b7a3e; font-size:14px;'>© 2025 EcoScore.AI — All rights reserved</div>", unsafe_allow_html=True)

