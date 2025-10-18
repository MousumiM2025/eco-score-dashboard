# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from textwrap import dedent

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="EcoScore.AI", page_icon="🌿", layout="wide")

# -----------------------
# Helper: flexible column finder
# -----------------------
def find_col(df, candidates):
    cols = [c.strip() for c in df.columns]
    low_map = {c.lower(): c for c in cols}
    for cand in candidates:
        key = cand.strip().lower()
        if key in low_map:
            return low_map[key]
    # fallback substring match
    for cand in candidates:
        cl = cand.strip().lower()
        for c in cols:
            if cl in c.lower():
                return c
    return None

# -----------------------
# Load data (robust)
# -----------------------
@st.cache_data
def load_data(path="ecoscore_data_extended_v2.csv"):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load dataset 'ecoscore_data_extended_v2.csv': {e}")
    st.stop()

# -----------------------
# Detect/normalize columns
# -----------------------
COL_PRODUCT = find_col(df, ["Product", "product", "Product Name"])
COL_CATEGORY = find_col(df, ["Category", "category"])
COL_PRICE = find_col(df, ["Price_USD", "Price", "Price (USD)", "price_usd"])
COL_ECOSCORE = find_col(df, ["EcoScore", "ecoscore"])
COL_CARBON = find_col(df, ["Carbon_Intensity_gCO2e", "Adj_Carbon_Intensity", "Carbon_Intensity", "carbon"])
COL_PACK = find_col(df, ["Packaging", "Packaging_Type", "Packaging Type"])
COL_ING = find_col(df, ["Main_Ingredients", "Ingredients"])
COL_COUNTRY = find_col(df, ["Country", "country"])
COL_RECYCLE = find_col(df, ["Recyclability_Score", "Recyclability"])

# Basic required columns check
required = [COL_PRODUCT, COL_CATEGORY]
if not all(required):
    st.error("CSV must include Product and Category columns (or similar). Found columns: " + ", ".join(df.columns))
    st.stop()

# Ensure numeric fields exist and coerce
if COL_PRICE:
    df[COL_PRICE] = pd.to_numeric(df[COL_PRICE], errors="coerce")
if COL_ECOSCORE:
    df[COL_ECOSCORE] = pd.to_numeric(df[COL_ECOSCORE], errors="coerce")
if COL_CARBON:
    df[COL_CARBON] = pd.to_numeric(df[COL_CARBON], errors="coerce")
if COL_RECYCLE:
    df[COL_RECYCLE] = pd.to_numeric(df[COL_RECYCLE], errors="coerce")

# Fill missing optional columns with sensible defaults
if not COL_PACK:
    df["Packaging"] = "Unknown"
    COL_PACK = "Packaging"
if not COL_ING:
    df["Main_Ingredients"] = ""
    COL_ING = "Main_Ingredients"
if not COL_COUNTRY:
    df["Country"] = "USA"
    COL_COUNTRY = "Country"
if not COL_RECYCLE:
    # default recyclability mapping on packaging
    df["Recyclability_Score"] = 60
    COL_RECYCLE = "Recyclability_Score"

# If adjusted carbon already present, use it preferentially
if "Adj_Carbon_Intensity" in df.columns and COL_CARBON != "Adj_Carbon_Intensity":
    df["Adj_Carbon_Intensity"] = pd.to_numeric(df["Adj_Carbon_Intensity"], errors="coerce")
else:
    # create Adj_Carbon_Intensity if not present by using Carbon and optional country factors
    if "Adj_Carbon_Intensity" not in df.columns:
        df["Adj_Carbon_Intensity"] = df[COL_CARBON].copy()

# -----------------------
# Packaging recyclability mapping (fallbacks)
# -----------------------
pack_map = {
    "Plastic": 40,
    "Recycled Plastic": 65,
    "Glass": 90,
    "Aluminum": 85,
    "Paper": 88,
    "Cardboard": 88,
    "Bioplastic": 70,
    "Pump Bottle": 50,
    "Aerosol Can": 30,
    "Refill Pouch": 80,
    "Tube": 45,
    "Unknown": 60
}
# If Recyclability_Score column missing, compute from packaging
if COL_RECYCLE not in df.columns or df[COL_RECYCLE].isnull().all():
    df["Recyclability_Score"] = df[COL_PACK].map(lambda x: pack_map.get(str(x), 60))
    COL_RECYCLE = "Recyclability_Score"

# -----------------------
# Country emission factor mapping (if not present)
# -----------------------
# If CSV includes Country_Emission_Factor, respect it, otherwise map by country
if "Country_Emission_Factor" not in df.columns:
    country_factor_map = {
        "USA": 1.0, "France": 0.6, "Germany": 0.8, "India": 1.5,
        "China": 1.8, "Canada": 0.7, "Brazil": 0.9, "Japan": 1.0,
    }
    df["Country_Emission_Factor"] = df[COL_COUNTRY].map(lambda c: country_factor_map.get(c, 1.0))

# compute adjusted carbon if not already meaningful
if "Adj_Carbon_Intensity" not in df.columns or df["Adj_Carbon_Intensity"].isnull().all():
    df["Adj_Carbon_Intensity"] = (df[COL_CARBON] * df["Country_Emission_Factor"]).round(1)

# -----------------------
# UI: Header
# -----------------------
col1, col2 = st.columns([1, 6])
with col1:
    # simple logo placeholder (no local file required)
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/70/Leaf_icon_green.svg", width=100)
with col2:
    st.markdown("<h1 style='color:#0c6b2f; font-size:38px; font-weight:700;'>EcoScore.AI Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#2b7a3e;'>Compare sustainability, packaging, carbon intensity and price across consumer products.</p>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------
# Sidebar: Filters
# -----------------------
st.sidebar.header("Filters & Tools")

# Category filter
categories = sorted(df[COL_CATEGORY].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category", ["All"] + categories, index=0)

df_view = df.copy()
if selected_category != "All":
    df_view = df_view[df_view[COL_CATEGORY] == selected_category]

# EcoScore range slider (detect min/max)
if COL_ECOSCORE in df_view.columns:
    min_s = int(df_view[COL_ECOSCORE].min(skipna=True) if not df_view[COL_ECOSCORE].isna().all() else 0)
    max_s = int(df_view[COL_ECOSCORE].max(skipna=True) if not df_view[COL_ECOSCORE].isna().all() else 100)
    eco_min, eco_max = st.sidebar.slider("EcoScore range", 0, 100, (min_s, max_s))
    df_view = df_view[(df_view[COL_ECOSCORE] >= eco_min) & (df_view[COL_ECOSCORE] <= eco_max)]
else:
    eco_min, eco_max = 0, 100

# Price range slider
if COL_PRICE in df_view.columns:
    p_min = float(df_view[COL_PRICE].min(skipna=True))
    p_max = float(df_view[COL_PRICE].max(skipna=True))
    pr_min, pr_max = st.sidebar.slider("Price range (USD)", float(round(p_min, 2)), float(round(p_max, 2)), (float(round(p_min, 2)), float(round(p_max, 2))))
    df_view = df_view[(df_view[COL_PRICE] >= pr_min) & (df_view[COL_PRICE] <= pr_max)]
else:
    pr_min, pr_max = 0.0, 0.0

# Country filter
countries = sorted(df_view[COL_COUNTRY].dropna().unique().tolist())
sel_countries = st.sidebar.multiselect("Country of origin (optional)", options=countries, default=countries)
if sel_countries:
    df_view = df_view[df_view[COL_COUNTRY].isin(sel_countries)]

st.sidebar.markdown("---")
st.sidebar.markdown("Tip: Use the **What-If Simulator** (below) to see how packaging or country changes affect carbon intensity and EcoScore.")

# -----------------------
# Main area: selection & table
# -----------------------
st.subheader("Filtered product set")
display_cols = []
# prefer friendly names if available
col_map = {
    COL_PRODUCT: "Product",
    COL_CATEGORY: "Category",
    COL_PRICE: "Price (USD)",
    COL_ECOSCORE: "EcoScore",
    "Adj_Carbon_Intensity": "Adj_Carbon_Intensity",
    COL_PACK: "Packaging",
    COL_ING: "Main_Ingredients",
    COL_COUNTRY: "Country",
    COL_RECYCLE: "Recyclability_Score"
}
for k, nice in col_map.items():
    if k and k in df_view.columns:
        display_cols.append(k)

if display_cols:
    # show the table with formatted numeric columns
    table = df_view[display_cols].copy()
    rename_map = {k: v for k, v in col_map.items() if k in table.columns}
    table = table.rename(columns=rename_map)
    fmt = {}
    if "Price (USD)" in table.columns:
        fmt["Price (USD)"] = "${:,.2f}".format
    if "Adj_Carbon_Intensity" in table.columns:
        fmt["Adj_Carbon_Intensity"] = "{:.1f} gCO₂e".format
    if "EcoScore" in table.columns:
        fmt["EcoScore"] = "{:.0f}".format
    st.dataframe(table.style.format(fmt), use_container_width=True)
else:
    st.info("No displayable columns found in the filtered dataset.")

# -----------------------
# Compare two products (side-by-side)
# -----------------------
st.markdown("## 🔁 Compare Two Products")
prod_list = df_view[COL_PRODUCT].dropna().unique().tolist()
if len(prod_list) < 2:
    st.info("Not enough products available for comparison with current filters.")
else:
    c1, c2 = st.columns(2)
    with c1:
        p1 = st.selectbox("Product 1", prod_list, index=0)
    with c2:
        p2 = st.selectbox("Product 2", prod_list, index=1 if len(prod_list) > 1 else 0)

    if p1 and p2:
        rows = df[df[COL_PRODUCT].isin([p1, p2])].copy()
        # build comparison table
        comp_cols = []
        for k, nice in col_map.items():
            if k and k in rows.columns:
                comp_cols.append(k)
        comp = rows[comp_cols].copy()
        comp = comp.rename(columns={k: col_map[k] for k in comp_cols})
        # nice formatting
        fmt_comp = {}
        if "Price (USD)" in comp.columns:
            fmt_comp["Price (USD)"] = "${:,.2f}".format
        if "Adj_Carbon_Intensity" in comp.columns:
            fmt_comp["Adj_Carbon_Intensity"] = "{:.1f} gCO₂e".format
        st.dataframe(comp.style.format(fmt_comp), use_container_width=True)

        # quick textual insights comparison
        for idx, r in rows.iterrows():
            name = r[COL_PRODUCT]
            eco = r[COL_ECOSCORE] if COL_ECOSCORE in r else "N/A"
            carbon = r.get("Adj_Carbon_Intensity", r.get(COL_CARBON, "N/A"))
            recycle = r.get(COL_RECYCLE, "N/A")
            st.write(f"**{name}** — EcoScore: {eco}, Adjusted Carbon: {carbon}, Recyclability: {recycle}")

# -----------------------
# What-if LCA-like simulator
# -----------------------
st.markdown("## 🧪 What-If LCA Simulator (Packaging & Country)")
st.markdown("Pick one product, change packaging or country, and see estimated effects on carbon intensity and EcoScore.")

sel_prod = st.selectbox("Select product to simulate", df[COL_PRODUCT].unique())
if sel_prod:
    row = df[df[COL_PRODUCT] == sel_prod].iloc[0]
    base_price = row[COL_PRICE] if COL_PRICE in row else None
    base_eco = row[COL_ECOSCORE] if COL_ECOSCORE in row else None
    base_carbon = row.get("Adj_Carbon_Intensity", row.get(COL_CARBON, None))
    base_country = row[COL_COUNTRY] if COL_COUNTRY in row else "USA"
    base_pack = row[COL_PACK] if COL_PACK in row else "Unknown"
    base_recycle = row[COL_RECYCLE] if COL_RECYCLE in row else pack_map.get(base_pack, 60)

    st.write(f"**Base** — Product: {sel_prod}")
    st.write(f"- Country: **{base_country}**; Packaging: **{base_pack}**; EcoScore: **{base_eco}**; Adjusted Carbon: **{base_carbon} gCO₂e**; Recyclability: **{base_recycle}/100**")

    # simulate new packaging
    new_pack = st.selectbox("New packaging material", options=list(pack_map.keys()), index=list(pack_map.keys()).index(base_pack) if base_pack in pack_map else 0)
    new_country = st.selectbox("New country of origin (affects emissions factor)", options=list(df["Country"].unique()), index=list(df["Country"].unique()).index(base_country) if base_country in df["Country"].unique() else 0)
    country_factor_map = {c: f for c, f in zip(df["Country"].unique(), df["Country_Emission_Factor"].unique())} if "Country_Emission_Factor" in df.columns else None
    # allow tweak
    tweak = st.slider("Manual emissions multiplier (simulate cleaner/dirter manufacturing or transport)", 0.5, 2.0, 1.0, 0.05)

    # compute simulated values
    new_recycle = pack_map.get(new_pack, 60)
    # get base country factor
    base_country_factor = float(row.get("Country_Emission_Factor", 1.0))
    # get new country factor (if mapping known) else fallback 1.0
    new_country_factor = float(df.loc[df[COL_COUNTRY] == new_country, "Country_Emission_Factor"].iloc[0]) if new_country in df[COL_COUNTRY].values else base_country_factor

    # heuristic: packaging effect reduces or increases carbon proportional to (100 - recyclability)/100
    # Keep formula simple and conservative for demo:
    pack_effect_base = (100 - float(base_recycle)) / 100.0
    pack_effect_new = (100 - float(new_recycle)) / 100.0

    # base raw carbon (before country factor) approximate:
    raw_base = base_carbon / base_country_factor if base_country_factor else base_carbon

    raw_new = raw_base * (pack_effect_new / pack_effect_base if pack_effect_base != 0 else 1.0)
    new_carbon = raw_new * new_country_factor * tweak
    # clamp
    if new_carbon < 0:
        new_carbon = 0.0

    # crude EcoScore adjustment: higher recyclability helps, higher carbon reduces score
    eco_delta = (new_recycle - base_recycle) * 0.15 - (new_carbon - base_carbon) * 0.02
    sim_ecoscore = None
    if base_eco is not None and not pd.isna(base_eco):
        sim_ecoscore = min(100, max(0, base_eco + eco_delta))

    st.markdown("### Simulation Results")
    st.write(f"- **Estimated new adjusted carbon intensity:** **{new_carbon:.1f} gCO₂e** (was {base_carbon} gCO₂e)")
    if sim_ecoscore is not None:
        st.write(f"- **Estimated new EcoScore:** **{sim_ecoscore:.1f} / 100** (was {base_eco})")
    st.write(f"- **New recyclability score:** {new_recycle}/100 (was {base_recycle}/100)")
    st.markdown("---")
    st.markdown("**Notes:** This is a simple illustrative simulator for exploring trade-offs. For production-level LCA you should integrate validated lifecycle assessment data and unit functional equivalence assumptions.")

# -----------------------
# Automated carbon explanation for filtered set
# -----------------------
st.markdown("## 🔎 Carbon Insights")
if "Adj_Carbon_Intensity" in df_view.columns:
    avg_cat = df_view["Adj_Carbon_Intensity"].mean()
    st.write(f"Category average adjusted carbon intensity (based on filters): **{avg_cat:.1f} gCO₂e**")
    high = df_view[df_view["Adj_Carbon_Intensity"] > avg_cat]
    if not high.empty:
        st.warning(f"{len(high)} product(s) in the current view have higher-than-average adjusted carbon intensity.")
        # show top 5 highest
        top_high = high.sort_values("Adj_Carbon_Intensity", ascending=False).head(5)
        st.table(top_high[[COL_PRODUCT, COL_CATEGORY, "Adj_Carbon_Intensity", COL_PACK, COL_RECYCLE]].rename(columns={
            COL_PRODUCT: "Product", COL_CATEGORY: "Category", COL_PACK: "Packaging", COL_RECYCLE: "Recyclability"
        }))
        st.info(dedent("""\
            Why might carbon intensity be high?
            - Energy-intensive manufacturing processes (e.g., high-temperature chemical synthesis)
            - Heavy or non-recyclable packaging materials (low recyclability)
            - Long-distance transport or supply chain complexity
            - Low use of renewable energy in the country of production
            Use the What-If Simulator to test packaging or country changes."""))
    else:
        st.success("No products above the filtered category average carbon intensity.")

# -----------------------
# Explanation / methodology
# -----------------------
with st.expander("How EcoScore is calculated (methodology & sources)", expanded=False):
    st.markdown(dedent("""\
        **EcoScore (0–100)** in this prototype is a composite indicator combining:
        - Ingredient safety & biodegradability (~40%) — hazard scoring from ingredient lists (prototype)
        - Carbon intensity (~30%) — estimated lifecycle emissions (g CO₂e per unit, adjusted by country factors)
        - Packaging sustainability (~20%) — recyclability & material type
        - Price fairness/accessibility (~10%) — normalized to category baseline

        **Data & notes:** The dataset used here is synthetic/illustrative (for demo). For production, replace with verified LCA data, manufacturer disclosures, OpenBeauty/OpenFood records, and validated ingredient hazard lists (e.g., EWG).
        """))

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.markdown("<div style='text-align:center; color:#2b7a3e; font-size:13px;'>© 2025 EcoScore.AI — All rights reserved</div>", unsafe_allow_html=True)

