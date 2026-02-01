import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 Salary Overview")

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

col1, col2, col3 = st.columns(3)

col1.metric("Average Salary (USD)", f"${df['usd'].mean():,.0f}")
col2.metric("Median Salary (USD)", f"${df['usd'].median():,.0f}")
col3.metric("Total Records", len(df))

fig = px.histogram(
    df,
    x="usd",
    nbins=40,
    title="Salary Distribution",
    labels={"usd": "Annual Salary (USD)"},
    color_discrete_sequence=["#1f77b4"]
)

st.plotly_chart(fig, use_container_width=True)
