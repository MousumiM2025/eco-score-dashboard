import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

# -----------------------
# Helper: flexible column finder
# -----------------------
def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
        # case-insensitive
        for col in df.columns:
            if col.strip().lower() == c.strip().lower():
                return col
    return None

# -----------------------
# Load data (cached)
# -----------------------
@st.cache_data
def load_data(path="ecoscore_data_2023.csv"):
    df = pd.read_csv(path)
    # normalize column names by stripping whitespace
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = load_data("ecoscore_data_2023.csv")
except Exception as e:
    st.error(f"Could not load CSV file: {e}")
    st.stop()

# -----------------------
# Detect important columns (flexible)
# -----------------------
COL_CATEGORY = find_col(df, ["Category", "category"])
COL_PRODUCT = find_col(df, ["Product", "product", "Product Name", "product_name"])
COL_BRAND = find_col(df, ["Brand", "brand"])
COL_PRICE = find_col(df, ["Price_USD", "Price (USD)", "Price_USD ", "price_usd", "Price"])
COL_ECOSCORE = find_col(df, ["EcoScore", "ecoscore", "Eco Score", "ecoscore_score"])
COL_CARBON = find_col(df, ["Carbon_Intensity_gCO2eq", "Carbon_Intensity_kgCO2e", "Carbon_Intensity_gCO2", "carbon_intensity_gco2eq", "Carbon_Intensity", "carbon_intensity"])
COL_PACK = find_col(df, ["Packaging_Type", "Packaging", "packaging"])
COL_MAIN_ING = find_col(df, ["Main_Ingredients", "Main Ingredients", "Ingredients", "main_ingredients"])

# Also find ingredient_1..ingredient_5 if present
ingredient_cols = [c for c in df.columns if c.lower().startswith("ingredient")]
ingredient_cols = sorted(ingredient_cols)[:5]  # keep up to 5

# validate essential columns
essential = [COL_CATEGORY, COL_PRODUCT, COL_PRICE, COL_ECOSCORE, COL_CARBON]
if not all(essential):
    st.error("CSV is missing one of the required columns. Required (any of): Category, Product, Price, EcoScore, Carbon_Intensity.\n\n"
             "Found columns: " + ", ".join(df.columns))
    st.stop()

# Ensure numeric types
df[COL_PRICE] = pd.to_numeric(df[COL_PRICE], errors="coerce")
df[COL_ECOSCORE] = pd.to_numeric(df[COL_ECOSCORE], errors="coerce")
df[COL_CARBON] = pd.to_numeric(df[COL_CARBON], errors="coerce")

# -----------------------
# Page layout
# -----------------------
st.set_page_config(page_title="EcoScore Comparison", page_icon="🌿", layout="wide")
st.title("🌿 EcoScore Dashboard — Compare products (2023 price baseline)")

st.markdown(
    "Select a product **category** and then one or more **products** to compare. "
    "The table and charts show Price (USD), EcoScore, Carbon Intensity, Packaging, and the top ingredients."
)

# -----------------------
# Category selector
# -----------------------
categories = df[COL_CATEGORY].dropna().unique()
selected_category = st.selectbox("Select Category", sorted(categories))

# Filter to category
df_cat = df[df[COL_CATEGORY] == selected_category].copy()
if df_cat.empty:
    st.warning("No products found in this category.")
    st.stop()

# -----------------------
# Product multiselect (searchable)
# -----------------------
product_list = sorted(df_cat[COL_PRODUCT].astype(str).unique())
selected_products = st.multiselect("Select products to compare (searchable):", product_list, default=product_list[:2])

if not selected_products:
    st.info("Select one or more products to compare.")
    st.stop()

compare_df = df_cat[df_cat[COL_PRODUCT].isin(selected_products)].copy()

# -----------------------
# Prepare Ingredients columns for display
# -----------------------
def extract_ingredients(row):
    # If individual ingredient columns exist, use them
    if ingredient_cols:
        ing = [str(row.get(c, "")).strip() for c in ingredient_cols if str(row.get(c, "")).strip()]
        # pad/truncate to 5
        ing = ing[:5] + [""] * max(0, 5 - len(ing))
        return ing
    # Else, parse Main_Ingredients comma-separated string
    if COL_MAIN_ING and pd.notna(row.get(COL_MAIN_ING)):
        parts = [p.strip() for p in str(row.get(COL_MAIN_ING)).split(",") if p.strip()]
        parts = parts[:5] + [""] * max(0, 5 - len(parts))
        return parts
    # fallback: empty list
    return [""] * 5

# Build a display dataframe with requested columns
display_cols = {
    "Product Name": COL_PRODUCT,
    "Brand": COL_BRAND or "",
    "Price (USD)": COL_PRICE,
    "EcoScore": COL_ECOSCORE,
    "Carbon Intensity (gCO₂e)": COL_CARBON,
    "Packaging": COL_PACK or "",
}

# create display DataFrame
rows = []
for _, r in compare_df.iterrows():
    ing_list = extract_ingredients(r)
    row = {
        "Product Name": r[COL_PRODUCT],
        "Brand": r[COL_BRAND] if COL_BRAND else "",
        "Price (USD)": r[COL_PRICE],
        "EcoScore": r[COL_ECOSCORE],
        "Carbon Intensity (gCO₂e)": r[COL_CARBON],
        "Packaging": r[COL_PACK] if COL_PACK else "",
        "Ingredient 1": ing_list[0],
        "Ingredient 2": ing_list[1],
        "Ingredient 3": ing_list[2],
        "Ingredient 4": ing_list[3],
        "Ingredient 5": ing_list[4],
    }
    rows.append(row)

comp_display_df = pd.DataFrame(rows)

# Reorder columns for nicer display
comp_display_df = comp_display_df[
    ["Product Name", "Brand", "Price (USD)", "EcoScore", "Carbon Intensity (gCO₂e)", "Packaging",
     "Ingredient 1", "Ingredient 2", "Ingredient 3", "Ingredient 4", "Ingredient 5"]
]

# -----------------------
# Show comparison table
# -----------------------
st.markdown("### 🧾 Comparison Table")
st.dataframe(comp_display_df.style.format({
    "Price (USD)": "${:,.2f}".format,
    "EcoScore": "{:.0f}",
    "Carbon Intensity (gCO₂e)": "{:.1f}"
}), use_container_width=True)

# Download button for the comparison CSV
csv_buffer = StringIO()
comp_display_df.to_csv(csv_buffer, index=False)
csv_bytes = csv_buffer.getvalue().encode()
st.download_button("⬇️ Download comparison CSV", data=csv_bytes, file_name="ecoscore_comparison.csv", mime="text/csv")

# -----------------------
# Category summary (averages, totals)
# -----------------------
st.markdown("### 📊 Category Summary (entire category)")

avg_ecoscore = df_cat[COL_ECOSCORE].mean()
avg_price = df_cat[COL_PRICE].mean()
total_carbon = df_cat[COL_CARBON].sum()
median_price = df_cat[COL_PRICE].median()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average EcoScore", f"{avg_ecoscore:.1f}")
col2.metric("Average Price (USD)", f"${avg_price:.2f}")
col3.metric("Median Price (USD)", f"${median_price:.2f}")
col4.metric("Total Carbon Intensity (sum, gCO₂e)", f"{total_carbon:.0f}")

st.markdown("- Best products in this category (by EcoScore):")
top3 = df_cat.sort_values(by=COL_ECOSCORE, ascending=False).head(3)
for i, (_, r) in enumerate(top3.iterrows(), start=1):
    st.write(f"{i}. **{r[find_col(df,['Product','product','Product Name'])]}** — EcoScore: {r[COL_ECOSCORE]} — Price: ${r[COL_PRICE]:.2f}")

# -----------------------
# Scatter Chart: EcoScore vs Price (for selected products)
# -----------------------
st.markdown("### 📈 Selected Products: EcoScore vs Price (bubble size = carbon intensity)")

fig = px.scatter(
    comp_display_df,
    x="Price (USD)",
    y="EcoScore",
    color="Brand",
    size="Carbon Intensity (gCO₂e)",
    hover_data=["Product Name", "Brand", "Packaging",
                "Ingredient 1", "Ingredient 2", "Ingredient 3"],
    text="Product Name",
    title=f"{selected_category}: EcoScore vs Price (selected products)"
)
fig.update_traces(textposition="top center")
st.plotly_chart(fig, use_container_width=True, height=600)

# -----------------------
# Insights summary for selected products
# -----------------------
st.markdown("### 🌟 Quick Insights (selected products)")
best_overall = comp_display_df.loc[comp_display_df["EcoScore"].idxmax()]
lowest_carbon = comp_display_df.loc[comp_display_df["Carbon Intensity (gCO₂e)"].idxmin()]
best_value = comp_display_df.loc[(comp_display_df["EcoScore"] / comp_display_df["Price (USD)"]).idxmax()]

c1, c2, c3 = st.columns(3)
c1.metric("Best EcoScore", best_overall["Product Name"], f"{best_overall['EcoScore']}/100")
c2.metric("Lowest Carbon", lowest_carbon["Product Name"], f"{lowest_carbon['Carbon Intensity (gCO₂e)']:.1f} gCO₂e")
c3.metric("Best EcoScore per $", best_value["Product Name"], f"{best_value['EcoScore']:.1f} / ${best_value['Price (USD)']:.2f}")

# -----------------------
# Scoring transparency footer
# -----------------------
st.markdown("---")
st.markdown("### 📘 Scoring methodology & data sources")
st.markdown(
    "- **EcoScore** (0–100): composite of ingredient safety (40%), carbon intensity (30%), packaging sustainability (20%), price fairness (10%).\n"
    "- **Carbon Intensity** is expressed in grams CO₂e per unit (2023 baseline estimates).\n"
    "- **Price** values are 2023 average retail prices (USD).\n"
    "- **Ingredients** are the top-listed components (up to 5) from product datasheets / OpenBeautyFacts / EWG / manufacturer labels.\n"
    "\n**Data sources & notes:** Open Beauty Facts, Open Food Facts, EWG Skin Deep, retailer baselines price (2023), company disclosures. This is a prototype — please verify data for high-stakes decisions."
)

st.caption("Built with ❤ by EcoScore.AI — update the CSV to add products or categories.")


