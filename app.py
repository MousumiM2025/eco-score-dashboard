# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
import os
import datetime

# -----------------------
# Utilities
# -----------------------
def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
        for col in df.columns:
            if col.strip().lower() == c.strip().lower():
                return col
    return None

@st.cache_data(ttl=3600)
def load_data(path="ecoscore_data_2023.csv"):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df

# -----------------------
# Load CSV (must be in same folder)
# -----------------------
try:
    df = load_data("ecoscore_data_2023.csv")
except Exception as e:
    st.set_page_config(page_title="EcoScore Dashboard - Error", page_icon="🌿", layout="wide")
    st.title("EcoScore Dashboard — Data load error")
    st.error(f"Could not load `ecoscore_data_2023.csv`: {e}")
    st.stop()

# -----------------------
# Detect columns (flexible)
# -----------------------
COL_CATEGORY = find_col(df, ["Category", "category"])
COL_PRODUCT = find_col(df, ["Product", "product", "Product Name", "product_name"])
COL_BRAND = find_col(df, ["Brand", "brand"])
COL_PRICE = find_col(df, ["Price_USD", "Price (USD)", "Price", "price_usd"])
COL_ECOSCORE = find_col(df, ["EcoScore", "ecoscore", "Eco Score"])
COL_CARBON = find_col(df, ["Carbon_Intensity_gCO2eq", "Carbon_Intensity_kgCO2e",
                          "Carbon_Intensity", "carbon_intensity"])
COL_PACK = find_col(df, ["Packaging_Type", "Packaging", "packaging", "Packaging Type"])
COL_MAIN_ING = find_col(df, ["Main_Ingredients", "Main Ingredients", "Ingredients", "ingredients"])
ingredient_cols = [c for c in df.columns if c.strip().lower().startswith("ingredient")]
ingredient_cols = sorted(ingredient_cols)[:5]

essential = [COL_CATEGORY, COL_PRODUCT, COL_PRICE, COL_ECOSCORE, COL_CARBON]
if not all(essential):
    st.set_page_config(page_title="EcoScore Dashboard - Schema Error", page_icon="🌿", layout="wide")
    st.title("CSV Schema Error")
    st.error("CSV must include: Category, Product, Price, EcoScore and Carbon_Intensity columns.")
    st.stop()

# coerce numeric
df[COL_PRICE] = pd.to_numeric(df[COL_PRICE], errors="coerce")
df[COL_ECOSCORE] = pd.to_numeric(df[COL_ECOSCORE], errors="coerce")
df[COL_CARBON] = pd.to_numeric(df[COL_CARBON], errors="coerce")

# -----------------------
# Page config & CSS (eco-green theme + font tweaks)
# -----------------------
st.set_page_config(page_title="EcoScore Dashboard", page_icon="🌿", layout="wide")

st.markdown(
    """
    <style>
    /* eco-green theme and readable fonts */
    html, body, [class*="css"] { font-family: Inter, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }
    .title { font-size:26px; font-weight:700; color:#0f5132; }
    .subtitle { font-size:13px; color:#4b5563; margin-top:6px; margin-bottom:14px; }
    .section-title { font-size:16px; font-weight:600; color:#0f5132; margin-top:10px; }
    .quick-insight-small { font-size:13px; color:#374151; font-weight:500; }
    .footer { font-size:12px; color:#6b7280; text-align:center; padding-top:8px; padding-bottom:16px; }
    /* subtle card background for table area */
    .stDataFrame, .element-container { background-color: #fbfdfb; }
    </style>
    """,
    unsafe_allow_html=True,
)

# disable right-click (basic deterrent)
st.components.v1.html(
    """
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    </script>
    """,
    height=0,
)

# Header
st.markdown('<div class="title">🌿 EcoScore Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Compare Price (2023 baseline), EcoScore, Carbon Intensity, Packaging, and Ingredients.</div>', unsafe_allow_html=True)

# -----------------------
# Sidebar: chart options & visitor setting
# -----------------------
st.sidebar.header("Chart & Display Options")
chart_size_metric = st.sidebar.selectbox("Bubble size metric", ("Carbon Intensity (gCO₂e)", "EcoScore", "Price (USD)"), index=0)
show_labels = st.sidebar.checkbox("Show labels on chart", value=True)
chart_mode = st.sidebar.selectbox("Chart mode", ("Price vs EcoScore (bubble)", "EcoScore vs Carbon (scatter)"))

st.sidebar.markdown("---")
st.sidebar.subheader("Visitor Tracking")
st.sidebar.markdown("Add `GA_MEASUREMENT_ID` in Streamlit Secrets to enable Google Analytics tracking (G-XXXXXXXXXX).")
# Visitor mode is fixed: show footer counter (local persist if possible)
vis_file_path = "/mnt/data/visits.txt"

def increment_local_counter(path=vis_file_path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        count = 0
        if os.path.exists(path):
            with open(path, "r") as f:
                txt = f.read().strip()
                if txt:
                    count = int(txt)
        count += 1
        with open(path, "w") as f:
            f.write(str(count))
        return count
    except Exception:
        return None

# increment local counter (best-effort)
local_count = increment_local_counter()

# If GA id provided in secrets, inject GA script
GA_ID = None
try:
    GA_ID = st.secrets.get("GA_MEASUREMENT_ID", None)
except Exception:
    GA_ID = None

if GA_ID:
    ga_snippet = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}');
    </script>
    """
    st.components.v1.html(ga_snippet, height=0)

# -----------------------
# Category & product selection
# -----------------------
categories = sorted(df[COL_CATEGORY].dropna().unique())
selected_category = st.selectbox("Select category", categories)
df_cat = df[df[COL_CATEGORY] == selected_category].copy()
product_list = sorted(df_cat[COL_PRODUCT].astype(str).unique())
selected_products = st.multiselect("Select products to compare (searchable)", product_list, default=product_list[:2])

if not selected_products:
    st.info("Please select one or more products to compare.")
    st.stop()

compare_df = df_cat[df_cat[COL_PRODUCT].isin(selected_products)].copy()

# -----------------------
# Build display table (extract up to 5 ingredients)
# -----------------------
def extract_ingredients(row):
    if ingredient_cols:
        ing = [str(row.get(c, "")).strip() for c in ingredient_cols if str(row.get(c, "")).strip()]
        ing = ing[:5] + [""] * max(0, 5 - len(ing))
        return ing
    if COL_MAIN_ING and pd.notna(row.get(COL_MAIN_ING)):
        parts = [p.strip() for p in str(row.get(COL_MAIN_ING)).split(",") if p.strip()]
        parts = parts[:5] + [""] * max(0, 5 - len(parts))
        return parts
    return [""] * 5

rows = []
for _, r in compare_df.iterrows():
    ing = extract_ingredients(r)
    rows.append({
        "Product Name": r[COL_PRODUCT],
        "Brand": r[COL_BRAND] if COL_BRAND else "",
        "Price (USD)": r[COL_PRICE],
        "EcoScore": r[COL_ECOSCORE],
        "Carbon (gCO₂e)": r[COL_CARBON],
        "Packaging": r[COL_PACK] if COL_PACK else "",
        "Ingredient 1": ing[0],
        "Ingredient 2": ing[1],
        "Ingredient 3": ing[2],
        "Ingredient 4": ing[3],
        "Ingredient 5": ing[4],
    })

display_df = pd.DataFrame(rows)[[
    "Product Name", "Brand", "Price (USD)", "EcoScore", "Carbon (gCO₂e)", "Packaging",
    "Ingredient 1", "Ingredient 2", "Ingredient 3", "Ingredient 4", "Ingredient 5"
]]

# -----------------------
# Comparison table (styled)
# -----------------------
st.markdown('<div class="section-title">🧾 Comparison Table</div>', unsafe_allow_html=True)
st.dataframe(display_df.style.format({
    "Price (USD)": "${:,.2f}".format,
    "EcoScore": "{:.0f}".format,
    "Carbon (gCO₂e)": "{:.1f}".format
}), use_container_width=True)

# CSV download
csv_buf = StringIO()
display_df.to_csv(csv_buf, index=False)
st.download_button("⬇️ Download comparison CSV", data=csv_buf.getvalue().encode(),
                   file_name="ecoscore_comparison.csv", mime="text/csv")

# -----------------------
# Category summary
# -----------------------
st.markdown('<div class="section-title">📊 Category Summary</div>', unsafe_allow_html=True)
avg_ecoscore = df_cat[COL_ECOSCORE].mean()
avg_price = df_cat[COL_PRICE].mean()
total_carbon = df_cat[COL_CARBON].sum()
median_price = df_cat[COL_PRICE].median()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average EcoScore", f"{avg_ecoscore:.1f}")
c2.metric("Average Price (USD)", f"${avg_price:.2f}")
c3.metric("Median Price (USD)", f"${median_price:.2f}")
c4.metric("Total Carbon (gCO₂e)", f"{total_carbon:.0f}")

st.write("Top 3 products by EcoScore in this category:")
top3 = df_cat.sort_values(by=COL_ECOSCORE, ascending=False).head(3)
for i, (_, r) in enumerate(top3.iterrows(), start=1):
    st.write(f"{i}. **{r[COL_PRODUCT]}** — EcoScore: {r[COL_ECOSCORE]} — Price: ${r[COL_PRICE]:.2f}")

# -----------------------
# Chart area
# -----------------------
st.markdown('<div class="section-title">📈 Comparison Chart</div>', unsafe_allow_html=True)
chart_df = display_df.copy()

# configure size metric
size_col = {"Carbon Intensity (gCO₂e)": "Carbon (gCO₂e)", "EcoScore": "EcoScore", "Price (USD)": "Price (USD)"}[chart_size_metric]

if chart_mode == "Price vs EcoScore (bubble)":
    fig = px.scatter(chart_df, x="Price (USD)", y="EcoScore", color="Brand", size=size_col,
                     hover_data=["Product Name", "Packaging"], text="Product Name" if show_labels else None,
                     title=f"{selected_category} — Price vs EcoScore")
else:
    fig = px.scatter(chart_df, x="EcoScore", y="Carbon (gCO₂e)", color="Brand", size=size_col,
                     hover_data=["Product Name", "Packaging"], text="Product Name" if show_labels else None,
                     title=f"{selected_category} — EcoScore vs Carbon Intensity")

fig.update_layout(title_x=0.5, legend_title_text="Brand", height=560)
fig.update_traces(marker=dict(line=dict(width=0.5, color="DarkSlateGrey")))
st.plotly_chart(fig, use_container_width=True)

# -----------------------
# Quick Insights (smaller product name font)
# -----------------------
st.markdown('<div class="section-title">🌟 Quick Insights (selected products)</div>', unsafe_allow_html=True)

best_overall = display_df.loc[display_df["EcoScore"].idxmax()]
lowest_carbon = display_df.loc[display_df["Carbon (gCO₂e)"].idxmin()]
best_value = display_df.loc[(display_df["EcoScore"] / display_df["Price (USD)"]).idxmax()]

col_a, col_b, col_c = st.columns(3)
col_a.markdown(f"<div style='font-size:13px; color:#065f46; font-weight:600;'>Best EcoScore</div><div class='quick-insight-small'>{best_overall['Product Name']} ({best_overall['EcoScore']}/100)</div>", unsafe_allow_html=True)
col_b.markdown(f"<div style='font-size:13px; color:#065f46; font-weight:600;'>Lowest Carbon</div><div class='quick-insight-small'>{lowest_carbon['Product Name']} ({lowest_carbon['Carbon (gCO₂e)']:.1f} gCO₂e)</div>", unsafe_allow_html=True)
col_c.markdown(f"<div style='font-size:13px; color:#065f46; font-weight:600;'>Best EcoScore per $</div><div class='quick-insight-small'>{best_value['Product Name']} (EcoScore/${best_value['Price (USD)']:.2f})</div>", unsafe_allow_html=True)

# -----------------------
# Footer: visitor count, GA note, copyright
# -----------------------
st.markdown("---")
footer_text = ""
if GA_ID:
    footer_text += "Tracking: Google Analytics active.  "
if local_count is not None:
    footer_text += f"Local page visits (persisted): {local_count}.  "
else:
    footer_text += "Local visit counter unavailable.  "

footer_text += "© 2025 EcoScore.AI — All rights reserved."

st.markdown(f"<div class='footer'>{footer_text}</div>", unsafe_allow_html=True)

# timestamp
st.caption(f"Dataset baseline: 2023 • Generated: {datetime.datetime.utcnow().date().isoformat()}")



