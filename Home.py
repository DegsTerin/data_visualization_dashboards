import streamlit as st
import pandas as pd
import plotly.express as px

# ===============================
# Page Configuration
# ===============================
st.set_page_config(
    page_title="Data Area Salary Dashboard",
    page_icon="📊",
    layout="wide",
)

px.defaults.template = "plotly_white"

# ===============================
# Data Loading
# ===============================

# Clear cache when switching data source manually
st.cache_data.clear()

@st.cache_data
def load_data():
    # URL (production / GitHub)
    # return pd.read_csv(
    #     "https://raw.githubusercontent.com/DegsTerin/Dashboard/refs/heads/main/Salaries.csv"
    # )

    # LOCAL (uncomment for local testing)
    return pd.read_csv("data/salaries.csv")

df = load_data()

# ===============================
# Dataset Validation
# ===============================
# Change: Update required column names to translated versions
REQUIRED_COLUMNS = {
    "Year", "Experience_Level", "Employment_Type", "Company_Size",
    "Salary_In_Usd", "Job_Title", "Remote_Ratio", "Employee_Residence_Iso3"
}

if not REQUIRED_COLUMNS.issubset(df.columns):
    st.error("The dataset does not contain all the necessary columns.")
    st.stop()

# ===============================
# Sidebar - Filters
# ===============================
st.sidebar.header("🔍 Filters")

years = st.sidebar.multiselect(
    "Year",
    sorted(df["Year"].unique()),
    default=sorted(df["Year"].unique())
)

experience_levels = st.sidebar.multiselect(
    "Experience Level",
    sorted(df["Experience_Level"].unique()),
    default=sorted(df["Experience_Level"].unique())
)

employment_types = st.sidebar.multiselect(
    "Employment Type",
    sorted(df["Employment_Type"].unique()),
    default=sorted(df["Employment_Type"].unique())
)

company_sizes = st.sidebar.multiselect(
    "Company Size",
    sorted(df["Company_Size"].unique()),
    default=sorted(df["Company_Size"].unique())
)

# ===============================
# Filter with cache
# ===============================
@st.cache_data
def filter_data(df, years, experience_levels, employment_types, company_sizes):
    return df[
        (df["Year"].isin(years)) &
        (df["Experience_Level"].isin(experience_levels)) &
        (df["Employment_Type"].isin(employment_types)) &
        (df["Company_Size"].isin(company_sizes))
    ]

df_filtered = filter_data(df, years, experience_levels, employment_types, company_sizes)

# ===============================
# Main Content
# ===============================
st.title("🎲 Data Area Salary Dashboard")
st.markdown("Use the filters on the left to refine the analysis.")

# ===============================
# KPIs
# ===============================
st.subheader("General Metrics (USD / year)")

if df_filtered.empty:
    st.warning("No data found with the selected filters.")
    average_salary = median_salary = maximum_salary = total_records = 0
    most_frequent_job_title = "-"
else:
    average_salary = df_filtered["Salary_In_Usd"].mean()
    median_salary = df_filtered["Salary_In_Usd"].median()
    maximum_salary = df_filtered["Salary_In_Usd"].max()
    total_records = len(df_filtered)
    most_frequent_job_title = df_filtered["Job_Title"].mode().iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Average Salary", f"${average_salary:,.0f}")
c2.metric("Median Salary", f"${median_salary:,.0f}")
c3.metric("Maximum Salary", f"${maximum_salary:,.0f}")
c4.metric("Total Records", f"{total_records:,}")
c5.metric("Most Frequent Job Title", most_frequent_job_title)

# ===============================
# Automatic Insight
# ===============================
if not df_filtered.empty and df_filtered["Year"].nunique() > 1:
    growth = (
        df_filtered.groupby("Year")["Salary_In_Usd"]
        .mean()
        .pct_change()
        .mean() * 100
    )

    if growth > 0:
        st.success(f"Average salary growth trend: {growth:.1f}% per year")
    else:
        st.warning(f"Average salary decrease trend: {growth:.1f}% per year")

st.divider()

# ===============================
# Outlier removal (visual)
# ===============================
if not df_filtered.empty:
    limit = df_filtered["Salary_In_Usd"].quantile(0.99)
    df_vis = df_filtered[df_filtered["Salary_In_Usd"] <= limit]
else:
    df_vis = df_filtered

# ===============================
# Charts
# ===============================
st.subheader("Charts")

col1, col2 = st.columns(2)

with col1:
    if not df_vis.empty:
        top_job_titles = (
            df_vis.groupby("Job_Title", as_index=False)["Salary_In_Usd"]
            .mean()
            .nlargest(10, "Salary_In_Usd")
            .sort_values("Salary_In_Usd")
        )

        fig = px.bar(
            top_job_titles,
            x="Salary_In_Usd",
            y="Job_Title",
            orientation="h",
            title="Top 10 Job Titles by Average Salary",
            labels={"Salary_In_Usd": "Average Annual Salary (USD)", "Job_Title": ""}
        )
        fig.update_traces(
            hovertemplate="Average salary: $%{x:,.0f}<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if not df_vis.empty:
        fig = px.histogram(
            df_vis,
            x="Salary_In_Usd",
            nbins=30,
            title="Salary Distribution (outliers removed)",
            labels={"Salary_In_Usd": "Annual Salary (USD)", "count": ""}
        )
        st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    if not df_vis.empty:
        remote_ratio = df_vis["Remote_Ratio"].value_counts().reset_index()
        remote_ratio.columns = ["type", "quantity"]

        fig = px.pie(
            remote_ratio,
            names="type",
            values="quantity",
            hole=0.5,
            title="Proportion of Employment Types"
        )
        fig.update_traces(
            textinfo="percent+label"
        )
        st.plotly_chart(fig, use_container_width=True)

with col4:
    df_ds = df_vis[df_vis["Job_Title"] == "Data Scientist"]

    if df_ds.empty:
        st.info("No Data Scientist data for current filters.")
    else:
        average_country_salary = (
            df_ds.groupby("Employee_Residence_Iso3", as_index=False)["Salary_In_Usd"]
            .mean()
        )

        fig = px.choropleth(
            average_country_salary,
            locations="Employee_Residence_Iso3",
            color="Salary_In_Usd",
            color_continuous_scale="RdYlGn",
            title="Average Data Scientist Salary by Country",
            labels={"Salary_In_Usd": "Average Salary (USD)"}
        )
        st.plotly_chart(fig, use_container_width=True)

# ===============================
# Job Title Comparison
# ===============================
st.subheader("Job Title Comparison")

if not df_filtered.empty:
    c1, c2 = st.columns(2)
    job_title_a = c1.selectbox("Job Title A", sorted(df["Job_Title"].unique()))
    job_title_b = c2.selectbox(
        "Job Title B",
        sorted(df["Job_Title"].unique()),
        index=1 if len(df["Job_Title"].unique()) > 1 else 0
    )

    comparison = (
        df_filtered[df_filtered["Job_Title"].isin([job_title_a, job_title_b])]
        .groupby("Job_Title")["Salary_In_Usd"]
        .agg(average="mean", median="median")
        .reset_index()
    )

    fig = px.bar(
        comparison,
        x="Job_Title",
        y=["average", "median"],
        barmode="group",
        title="Salary Comparison Between Job Titles (Average vs. Median)",
        labels={
            "value": "Annual Salary (USD)",
            "Job_Title": "",
            "variable": "Metric"
        }
    )

    fig.update_traces(
        hovertemplate="Salary: $%{y:,.0f}<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)

# ===============================
# Data Download
# ===============================
st.download_button(
    "📥 Download filtered data (CSV)",
    data=df_filtered.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)

# ===============================
# Table
# ===============================
st.subheader("Detailed Data")
st.dataframe(df_filtered, use_container_width=True)

# ===============================
# Documentation
# ===============================
with st.expander("ℹ️ About the Dashboard"):
    st.markdown("""
    • Data Source: Kaggle / GitHub
    • Values expressed in annual USD
    • Outliers removed at the 99th percentile for visualization only
    • Comparisons based on average and median
    """)