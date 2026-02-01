import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🏠 Work Mode Distribution")

# ===============================
# Data Loading
# ===============================

# Clear cache when switching data source manually
st.cache_data.clear()

@st.cache_data
def load_data():
    # URL (production / GitHub)
    #return pd.read_csv(
    #    "https://raw.githubusercontent.com/DegsTerin/data_visualization_dashboards/refs/heads/main/salaries.csv"
    #)

    # LOCAL (uncomment for local testing)
    return pd.read_csv("data/salaries.csv")

df = load_data()

work_mode = (
    df["remoto"]
    .value_counts()
    .reset_index()
)

work_mode.columns = ["Work Mode", "Count"]

fig = px.pie(
    work_mode,
    names="Work Mode",
    values="Count",
    hole=0.5,
    title="Work Mode Proportion",
    color_discrete_sequence=["#2ca02c", "#ff7f0e", "#1f77b4"]
)

st.plotly_chart(fig, use_container_width=True)
