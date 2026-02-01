import streamlit as st
import pandas as pd
import plotly.express as px

st.title("⚖️ Role Salary Comparison")

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

roles = sorted(df["cargo"].unique())

col1, col2 = st.columns(2)

role_a = col1.selectbox("Select first role", roles)
role_b = col2.selectbox("Select second role", roles, index=1)

comparison = (
    df[df["cargo"].isin([role_a, role_b])]
    .groupby("cargo")["usd"]
    .agg(mean="mean", median="median")
    .reset_index()
)

fig = px.bar(
    comparison,
    x="cargo",
    y=["mean", "median"],
    barmode="group",
    title="Average vs Median Salary by Role",
    labels={
        "value": "Annual Salary (USD)",
        "cargo": "Role",
        "variable": "Metric"
    },
    color_discrete_sequence=["#9467bd", "#8c564b"]
)

fig.update_traces(
    hovertemplate="Salary: $%{y:,.0f}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

# Extra insight
if role_a != role_b:
    avg_a = comparison.loc[comparison["cargo"] == role_a, "mean"].values[0]
    avg_b = comparison.loc[comparison["cargo"] == role_b, "mean"].values[0]

    diff = ((avg_a - avg_b) / avg_b) * 100

    st.info(
        f"On average, **{role_a}** earns "
        f"**{diff:.1f}% {'more' if diff > 0 else 'less'}** than **{role_b}**."
    )
