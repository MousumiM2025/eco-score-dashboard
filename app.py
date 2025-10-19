import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------
# Page Configuration
# --------------------------
st.set_page_config(page_title="EcoScore Dashboard", layout="wide")

st.markdown(
    """
    <h1 style='text-align: center; color: #2E8B57;'>🌿 EcoScore Dashboard</h1>
    """,
    unsafe_allow_html=True,
)

# --------------------------
# Load Data
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ecoscore_data_extended_v2.csv")
    df.columns = df.columns.str.strip()  # Clean up column names
    return df

df = load_data()

# Check key columns
required_cols = ["Product", "Category", "Price_USD", "EcoScore", "Carbon_Intensity_gCO2e"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"Missing columns in CSV: {missing}")
    st.stop()

# --------------------------
# Sidebar selection
# --------------------------
st.sidebar.header("🔍 Product Selection")

categories = sorted
