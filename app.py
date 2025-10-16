import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
import os
import datetime

# -----------------------
# Utility: find column from candidates (case/format tolerant)
# -----------------------
def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
        for col in df.columns:
            if col.strip().lower() == c.strip().lower():
                return col
    return None

# -----------------------
# Load CSV (cached)
# -----------------------
@st.cache_data(ttl=3600)
def load_data(path="ecoscore_data_2023.csv"):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = load_data("ecoscore_data_2023.csv")
except Exception as e:
    st.set_page_config(page_title="EcoScore Dashboard", page_icon="🌿", layout="wide")
    st.title("EcoScore Dashboard — Error")
    st.error(f"Could not load dataset `ecoscore_data_2023.csv`: {e}")
    st.stop()

# -----------------------
# Detect columns flexibly
# -----------------------
COL_CATEGORY = find_col(df, ["Category", "category"])
COL_PRODUCT = find_col(df, ["Product", "product", "Product Name", "product_name"])
COL_BRAND = find_col(df, ["Brand", "brand"])
COL_PRICE = find_col(df, ["Price_USD", "Price (USD)", "Price", "price_usd"])
COL_ECOSCORE = find_col(df, ["EcoScore", "ecoscore", "Eco Score"])
COL_CARBON = find_col(df, ["Carbon_Intensity_gCO2eq", "Carbon_Intensity_kgCO2e",
                          "Carbon_Intensity_gCO2", "Carbon_Intensity", "carbon_intensity"])
COL_PACK = find_col(df, ["Packaging_Type", "Packaging", "packaging", "Packaging Type"])
COL_MAIN_ING = find_col(df, ["Main_Ingredients", "Main Ingredients", "Ingredients", "ingredients"])

ingredient_cols = [c for c in df.columns if c.strip().lower().startswith("ingredient")]
ingredient_cols = sorted(ingredient_cols)[:5]

essential = [COL_CATEGORY, COL_PRODUCT, COL_PRICE, COL_ECOSCORE, COL_CARBON]
if not all(essential):
    st.set_page_config(page_title="EcoScore Dashboard", page_icon="🌿", layout="wide")
    st.title("EcoScore Dashboard — CSV Schema Error")
    st.error("CSV missing required columns. Required: Category, Product, Price (USD), EcoScore, Carbon_Intensity.")
    st.stop()

df[COL_PRICE] = pd.to_numeric(df[COL_PRICE], errors="coerce")
df[COL_ECOSCORE] = pd.to_numeric(df[COL_ECOSCORE], errors="coerce")
df[COL_CARBON] = pd.to_numeric(df[COL_CARBON], errors="coerce")

# -----------------------
# Page config & CSS tweaks
# -----------------------
st.set_page_config(page_title="EcoScore Dashboard", page_icon="🌿", layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: Inter, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    .big-title { font-size:28px; font-weight:700; margin-bottom:-6px; }
    .subtitle { font-size:14px; color:#4b5563; margin-top:-8px; margin-bottom:12px; }
    .metric-label { font-size:13px; color:#333; }
    .quick-insight-small { font-size:13px; color:#374151; font-weight:500; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="big-title">🌿 EcoScore Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Compare price (2023 baseline), EcoScore, carbon intensity, packaging, and ingredients.</div>', unsafe_allow_html=True)

# -----------------------
# Sidebar
# -----------------------
st.sidebar.header("Chart & Page Options")
chart_size_metric = st.sidebar.selectbox("Bubble size metric", 
    ("Carbon Intensity (gCO₂e)", "EcoScore", "Price (USD)"))
show_labels = st.sidebar.checkbox("Show labels on chart", value=True)
chart_mode = st.sidebar.selectbox("Chart mode", 
    ("Bubble chart (Price vs EcoScore)", "Scatter (EcoScore vs Carbon)"))

# Visitor counter
st.sidebar.markdown("---")
st.sidebar.subheader("Visitor tracking")
vis_mode = st.sidebar.selectbox("Visitor counting method", 
    ("Local counter (file)", "Google Analytics (recommended)", "Session only (local)"))

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

def get_local_count(path=vis_file_path):
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                txt = f.read().strip()
                if txt:
                    return int(txt)
        return 0
    except Exception:
        return None

if vis_mode == "Local counter (file)":
    vis_count = increment_local_counter()
elif vis_mode == "Session only (local)":
    if "session_visits" not in st.session_state:
        st.session_state["session_visits"] = 0
    st.session_state["session_visits"] += 1
    vis_count = st.session_state["session_visits"]
else:
    vis_count = None

if vis_count is not None:
    st.sidebar.markdown(f"**Page visits:** {vis_count}")
else:
    st.sidebar.markdown("**Page visits:** (Google Analytics active)")

# Inject Google Analytics script
GA_ID = st.secrets.get("GA_MEASUREMENT_ID", None) if "secrets" in dir(st) else None
if GA_ID and vis_mode == "Google Analytics (recommended)":
    ga_snippet = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}');
    </script>
    """
    st.components.v1.html(ga_snippet, height=0, width=0)

# -----------------------
# Category & product selection
# -----------------------
categories = sorted(df[COL_CATEGORY].dropna().unique())
selected_category = st.selectbox("Select category", categories)
df_cat = df[df[COL_CATEGORY] == selected_category].copy()
product_list = sorted(df_cat[COL_PRODUCT].astype(str).unique())
selected_products = st.multiselect("Select products to compare", product_list, default=product_list[:2])
if not selected_products:
    st.info("Please select one or more products.")
    st.stop()

compare_df = df_cat[df_cat[COL_PRODUCT].isin(selected_products)].copy()

# -----------------------
# Build display table
# -----------------------
def extract_ingredients(row):
    if ingredient_cols:
        ing = [str(row.get(c, "")).strip() for c in ingredient_cols if str(row.get(c, "")).strip()]
        return ing[:5] + [""] * max(0, 5 - len(ing))
    if COL_MAIN_ING and pd.notna(row.get(COL_MAIN_ING)):
        parts = [p.strip() for p in str(row.get(COL_MAIN_ING)).split(",") if p.strip()]
        return parts[:5] + [""] * max(0, 5 - len(parts))
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

display_df = pd.DataFrame(rows)

# -----------------------
# Show comparison table
# -----------------------
st.markdown("### 🧾 Comparison Table")
st.dataframe(display_df.style.format({
    "Price (USD)": "${:,.2f}".format,
    "EcoScore": "{:.0f}".format,
    "Carbon (gCO₂e)": "{:.1f}".format
}), use_container_width=True)

csv_buf = StringIO()
display_df.to_csv(csv_buf, index=False)
st.download_button("⬇️ Download comparison CSV", data=csv_buf.getvalue().encode(),
                   file_name="ecoscore_comparison.csv", mime="text/csv")

# -----------------------
# Category summary
# -----------------------
st.markdown("### 📊 Category Summary")
avg_ecoscore = df_cat[COL_ECOSCORE].mean()
avg_price = df_cat[COL_PRICE].mean()
total_carbon = df_cat[COL_CARBON].sum()
median_price = df_cat[COL_PRICE].median()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average EcoScore", f"{avg_ecoscore:.1f}")
col2.metric("Average Price (USD)", f"${avg_price:.2f}")
col3.metric("Median Price (USD)", f"${median_price:.2f}")
col4.metric("Total Carbon (gCO₂e)", f"{total_carbon:.0f}")

# -----------------------
# Chart
# -----------------------
st.markdown("### 📈 Comparison Chart")
chart_df = display_df.copy()
size_col = {"Carbon Intensity (gCO₂e)": "Carbon (gCO₂e)", "EcoScore": "EcoScore", "Price (USD)": "Price (USD)"}[chart_size_metric]
if chart_mode.startswith("Bubble"):
    fig = px.scatter(chart_df, x="Price (USD)", y="EcoScore", color="Brand", size=size_col,
                     hover_data=["Product Name", "Packaging"], text="Product Name" if show_labels else None,
                     title=f"{selected_category} — Price vs EcoScore")
else:
    fig = px.scatter(chart_df, x="EcoScore", y="Carbon (gCO₂e)", color="Brand", size=size_col,
                     hover_data=["Product Name", "Packaging"], text="Product Name" if show_labels else None,
                     title=f"{selected_category} — EcoScore vs Carbon Intensity")
fig.update_layout(title_x=0.5, legend_title_text="Brand", height=550)
st.plotly_chart(fig, use_container_width=True)

# -----------------------
# Quick Insights (smaller font)
# -----------------------
st.markdown("### 🌟 Quick Insights (selected products)")
best_overall = display_df.loc[display_df["EcoScore"].idxmax()]
lowest_carbon = display_df.loc[display_df["Carbon (gCO₂e)"].idxmin()]
best_value = display_df.loc[(display_df["EcoScore"] / display_df["Price (USD)"]).idxmax()]

c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='metric-label'>Best EcoScore:</div><div class='quick-insight-small'>{best_overall['Product Name']} ({best_overall['EcoScore']}/100)</div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-label'>Lowest Carbon:</div><div class='quick-insight-small'>{lowest_carbon['Product Name']} ({lowest_carbon['Carbon (gCO₂e)']:.1f} gCO₂e)</div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-label'>Best Value:</div><div class='quick-insight-small'>{best_value['Product Name']} (EcoScore/${best_value['Price (USD)']:.2f})</div>", unsafe_allow_html=True)

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.markdown("### 📘 Methodology & Data Sources")
st.markdown("""
- **EcoScore (0–100)** = Ingredient safety (40%) + Carbon intensity (30%) + Packaging sustainability (20%) + Price fairness (10%)  
- **Carbon Intensity** = gCO₂e per product unit, 2023 baseline  
- **Prices** = 2023 average U.S. retail prices (baseline)  
- **Ingredients** = extracted top-listed components (max 5)  
**Data sources:** Open Beauty Facts, EWG Skin Deep, Open Food Facts, and 2023 retail data.
""")
st.caption(f"Generated {datetime.datetime.utcnow().date().isoformat()} • Built with ❤ by EcoScore.AI — update CSV anytime.")

