# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --------- Page config ----------
st.set_page_config(page_title="EcoScore.AI — Comparison", page_icon="🌿", layout="wide")

# --------- Load CSV (robust) ----------
CSV_PATH = "ecoscore_data_extended_v2.csv"

@st.cache_data
def load_df(path):
    df = pd.read_csv(path)
    # normalize column names to lower and stripped (keep originals in a map)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df_raw = load_df(CSV_PATH)
except FileNotFoundError:
    st.error(f"CSV not found: {CSV_PATH}. Upload or place file in app folder.")
    st.stop()
except Exception as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()

# --------- column detection helpers ----------
def find_col(df, candidates):
    # candidates: list of name variants
    cols = df.columns.tolist()
    lowered = {c.strip().lower(): c for c in cols}
    for cand in candidates:
        key = cand.strip().lower()
        if key in lowered:
            return lowered[key]
    # substring fallback
    for cand in candidates:
        cl = cand.strip().lower()
        for c in cols:
            if cl in c.strip().lower():
                return c
    return None

# detect columns (common variants)
COL_PRODUCT = find_col(df_raw, ["product", "product_name", "name"])
COL_CATEGORY = find_col(df_raw, ["category", "category_name", "type"])
COL_PRICE = find_col(df_raw, ["price_usd", "price", "price ($)", "cost"])
COL_ECOSCORE = find_col(df_raw, ["ecoscore", "eco_score", "eco score", "score"])
COL_CARBON = find_col(df_raw, ["adj_carbon_intensity", "carbon_intensity_gco2e", "carbon_intensity", "carbon"])
COL_PACK = find_col(df_raw, ["packaging", "packaging_type", "package", "material"])
COL_ING = find_col(df_raw, ["main_ingredients", "ingredients", "ingredient"])
COL_RECYCLE = find_col(df_raw, ["recyclability_score", "recyclability"])
COL_COUNTRY = find_col(df_raw, ["country", "country_of_origin"])

# minimal checks
if not COL_PRODUCT or not COL_CATEGORY:
    st.error("CSV must include product and category columns (or similar). Detected columns: " + ", ".join(df_raw.columns))
    st.stop()

# create working df copy and coerce numeric columns
df = df_raw.copy()
if COL_PRICE:
    df[COL_PRICE] = pd.to_numeric(df[COL_PRICE], errors="coerce")
if COL_ECOSCORE:
    df[COL_ECOSCORE] = pd.to_numeric(df[COL_ECOSCORE], errors="coerce")
if COL_CARBON:
    df[COL_CARBON] = pd.to_numeric(df[COL_CARBON], errors="coerce")
if COL_RECYCLE:
    df[COL_RECYCLE] = pd.to_numeric(df[COL_RECYCLE], errors="coerce")

# if adjusted carbon exists under different name, already handled above via find_col

# --------- UI: header and instructions ----------
st.markdown(
    """
    <div style='display:flex;align-items:center;gap:16px'>
      <img src='https://upload.wikimedia.org/wikipedia/commons/7/70/Leaf_icon_green.svg' width='90' />
      <div>
        <h1 style='margin:0;color:#0c6b2f'>EcoScore.AI — Product Comparison</h1>
        <div style='color:#2b7a3e'>Pick a category and one or more products to compare EcoScore, carbon intensity and price.</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# --------- Selection controls ----------
categories = sorted(df[COL_CATEGORY].dropna().unique().tolist())
selected_category = st.selectbox("Select category", ["All"] + categories)

# filter list for product dropdown
if selected_category == "All":
    df_for_products = df
else:
    df_for_products = df[df[COL_CATEGORY] == selected_category]

products = sorted(df_for_products[COL_PRODUCT].dropna().unique().tolist())
selected_products = st.multiselect("Select products to compare (multi-select)", products[:3], options=products, default=products[:2] if products else [])

if not selected_products:
    st.info("Choose one or more products from the dropdown above to see comparisons.")
    st.stop()

df_sel = df_for_products[df_for_products[COL_PRODUCT].isin(selected_products)].copy()
if df_sel.empty:
    st.warning("No matching products found for selection.")
    st.stop()

# --------- Prepare tooltip fields ----------
# create a hover text column with packed info
def top_ingredients(text):
    if pd.isna(text):
        return ""
    parts = [p.strip() for p in str(text).split(",") if p.strip()]
    return ", ".join(parts[:5])

df_sel["_hover_text"] = df_sel[COL_PRODUCT].astype(str)
# include brand if exists
COL_BRAND = find_col(df, ["brand", "manufacturer"])
if COL_BRAND:
    df_sel["_hover_text"] += " — " + df_sel[COL_BRAND].astype(str)
# price
if COL_PRICE:
    df_sel["_hover_text"] += "<br>Price: $" + df_sel[COL_PRICE].astype(str)
# packaging
if COL_PACK:
    df_sel["_hover_text"] += "<br>Packaging: " + df_sel[COL_PACK].astype(str)
# recyclability
if COL_RECYCLE:
    df_sel["_hover_text"] += "<br>Recyclability: " + df_sel[COL_RECYCLE].astype(str)
# country
if COL_COUNTRY:
    df_sel["_hover_text"] += "<br>Country: " + df_sel[COL_COUNTRY].astype(str)
# ingredients
if COL_ING:
    df_sel["_hover_text"] += "<br>Top ingredients: " + df_sel[COL_ING].apply(top_ingredients)

# --------- Charts: main comparison (EcoScore vs Carbon) and Price view option ----------
st.markdown("### Visual comparison")

view_choice = st.radio("Choose chart", ("EcoScore vs Carbon Intensity", "EcoScore vs Price"))

if view_choice == "EcoScore vs Carbon Intensity":
    if not (COL_ECOSCORE and COL_CARBON):
        st.warning("Missing EcoScore or Carbon Intensity columns for this view.")
    else:
        fig = px.scatter(
            df_sel,
            x=COL_CARBON,
            y=COL_ECOSCORE,
            color=COL_PRODUCT,
            size=COL_ECOSCORE if COL_ECOSCORE in df_sel.columns else None,
            hover_name=COL_PRODUCT,
            hover_data={COL_CARBON: ':.1f', COL_ECOSCORE: ':.1f'},
            labels={COL_CARBON: "Carbon Intensity (gCO₂e)", COL_ECOSCORE: "EcoScore (0-100)"},
            title="EcoScore vs Carbon Intensity"
        )
        # add custom hover HTML (Plotly will show hover_data; also include our prepared text)
        # we can append hovertemplate for richer info
        hover_texts = df_sel["_hover_text"]
        fig.update_traces(hovertemplate=None)
        # attach hovertext as customdata
        fig.update_traces(customdata=hover_texts, selector=dict(mode='markers'))
        # set hovertemplate to show customdata first then x/y
        fig.update_traces(hovertemplate="<b>%{customdata}</b><br><br>%{x:.1f} gCO₂e (carbon)<br>%{y:.1f} EcoScore<extra></extra>")
        fig.update_layout(template="plotly_white", height=520)
        st.plotly_chart(fig, use_container_width=True)

else:  # EcoScore vs Price
    if not (COL_ECOSCORE and COL_PRICE):
        st.warning("Missing EcoScore or Price columns for this view.")
    else:
        fig = px.scatter(
            df_sel,
            x=COL_PRICE,
            y=COL_ECOSCORE,
            color=COL_PRODUCT,
            size=COL_ECOSCORE if COL_ECOSCORE in df_sel.columns else None,
            hover_name=COL_PRODUCT,
            hover_data={COL_PRICE: ':.2f', COL_ECOSCORE: ':.1f'},
            labels={COL_PRICE: "Price (USD)", COL_ECOSCORE: "EcoScore (0-100)"},
            title="EcoScore vs Price"
        )
        hover_texts = df_sel["_hover_text"]
        fig.update_traces(hovertemplate=None)
        fig.update_traces(customdata=hover_texts, selector=dict(mode='markers'))
        fig.update_traces(hovertemplate="<b>%{customdata}</b><br><br>$%{x:.2f} (price)<br>%{y:.1f} EcoScore<extra></extra>")
        fig.update_layout(template="plotly_white", height=520)
        st.plotly_chart(fig, use_container_width=True)

# --------- Table of selected products: price + top 5 ingredients ----------
st.markdown("### Selected products details")
table_cols = []
friendly_names = {}

# ensure we show product, price, top-5 ingredients, packaging, ecoscore, carbon
for col, nice in [
    (COL_PRODUCT, "Product"),
    (COL_PRICE, "Price (USD)"),
    (COL_ECOSCORE, "EcoScore"),
    (COL_CARBON, "Carbon (gCO₂e)"),
    (COL_PACK, "Packaging"),
    (COL_ING, "Top 5 Ingredients"),
]:
    if col and col in df_sel.columns:
        table_cols.append(col)
        friendly_names[col] = nice

# build table copy
table = df_sel[table_cols].copy()

# transform ingredients to top-5
if COL_ING and COL_ING in table.columns:
    table[COL_ING] = table[COL_ING].apply(lambda t: ", ".join([p.strip() for p in str(t).split(",")][:5]))

# rename for display
table = table.rename(columns=friendly_names)
# formatting
fmt = {}
if "Price (USD)" in table.columns:
    fmt["Price (USD)"] = "${:,.2f}".format
if "Carbon (gCO₂e)" in table.columns:
    fmt["Carbon (gCO₂e)"] = "{:.1f} gCO₂e".format
if "EcoScore" in table.columns:
    fmt["EcoScore"] = "{:.0f}".format

st.dataframe(table.style.format(fmt), use_container_width=True)

# --------- How EcoScore is measured ----------
st.markdown("---")
st.markdown("### How EcoScore is measured (prototype)")
st.markdown(
    """
    EcoScore in this prototype is a **composite** metric combining (example weights):
    - **Ingredient safety & biodegradability** — 40%  
    - **Carbon intensity** (gCO₂e per unit) — 30%  
    - **Packaging sustainability & recyclability** — 20%  
    - **Price fairness / accessibility** — 10%  

    This app uses estimated/synthetic values for demonstration. For production use, replace with validated lifecycle (LCA) and ingredient-hazard datasets.
    """
)

st.markdown("---")
st.caption("Dataset: ecoscore_data_extended_v2.csv • Prototype calculations for demonstration only")

