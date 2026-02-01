import streamlit as st
import pandas as pd
import plotly.express as px

# ===============================
# CONFIGURAÇÃO VISUAL GLOBAL
# ===============================
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

PALETA = px.colors.qualitative.Set2
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = PALETA

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

# ===============================
# VALIDAÇÃO
# ===============================
COLUNAS = {
    "ano", "senioridade", "contrato", "tamanho_empresa",
    "usd", "cargo", "remoto", "residencia_iso3"
}

if not COLUNAS.issubset(df.columns):
    st.error("Dataset inválido ou incompleto.")
    st.stop()

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("🔍 Filtros")

moeda = st.sidebar.radio("Moeda", ["USD", "EUR"], horizontal=True)

anos = st.sidebar.multiselect("Ano", sorted(df["ano"].unique()), default=df["ano"].unique())
senioridades = st.sidebar.multiselect("Senioridade", sorted(df["senioridade"].unique()), default=df["senioridade"].unique())
contratos = st.sidebar.multiselect("Contrato", sorted(df["contrato"].unique()), default=df["contrato"].unique())
tamanhos = st.sidebar.multiselect("Tamanho da empresa", sorted(df["tamanho_empresa"].unique()), default=df["tamanho_empresa"].unique())

# ===============================
# FILTRO COM CACHE
# ===============================
@st.cache_data
def filtrar(df, anos, senioridades, contratos, tamanhos):
    return df[
        df["ano"].isin(anos) &
        df["senioridade"].isin(senioridades) &
        df["contrato"].isin(contratos) &
        df["tamanho_empresa"].isin(tamanhos)
    ]

df_f = filtrar(df, anos, senioridades, contratos, tamanhos)

# Conversão simples USD → EUR (fixa, proposital)
TAXA_EUR = 0.92
df_f["salario"] = df_f["usd"] if moeda == "USD" else df_f["usd"] * TAXA_EUR

# ===============================
# TÍTULO
# ===============================
st.title("📊 Análise Avançada de Salários em Dados")
st.markdown("Dashboard interativo orientado a **decisão**, não apenas visualização.")

# ===============================
# KPIs
# ===============================
st.subheader("Indicadores principais")

if df_f.empty:
    st.warning("Nenhum dado com os filtros selecionados.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Salário médio", f"{df_f['salario'].mean():,.0f} {moeda}")
c2.metric("Salário mediano", f"{df_f['salario'].median():,.0f} {moeda}")
c3.metric("Máximo", f"{df_f['salario'].max():,.0f} {moeda}")
c4.metric("Registros", len(df_f))

st.divider()

# ===============================
# EVOLUÇÃO TEMPORAL (NOVO)
# ===============================
st.subheader("📈 Evolução salarial ao longo do tempo")

evolucao = df_f.groupby("ano")["salario"].mean().reset_index()

fig = px.line(
    evolucao,
    x="ano",
    y="salario",
    markers=True,
    title="Salário médio por ano",
    labels={"salario": f"Salário médio ({moeda})", "ano": ""}
)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# TOP CARGOS
# ===============================
st.subheader("🏆 Cargos mais bem pagos")

top_cargos = (
    df_f.groupby("cargo", as_index=False)["salario"]
    .mean()
    .nlargest(10, "salario")
    .sort_values("salario")
)

fig = px.bar(
    top_cargos,
    x="salario",
    y="cargo",
    orientation="h",
    title="Top 10 cargos por salário médio",
    labels={"salario": f"Salário médio ({moeda})", "cargo": ""}
)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# HEATMAP SENIORIDADE x EMPRESA (NOVO)
# ===============================
st.subheader("🔥 Senioridade x Tamanho da empresa")

heat = (
    df_f.groupby(["senioridade", "tamanho_empresa"])["salario"]
    .mean()
    .reset_index()
)

fig = px.density_heatmap(
    heat,
    x="tamanho_empresa",
    y="senioridade",
    z="salario",
    color_continuous_scale="Blues",
    title="Salário médio por senioridade e porte da empresa"
)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# COMPARAÇÃO ENTRE CARGOS (MELHORADA)
# ===============================
st.subheader("⚖️ Comparação entre cargos")

cargo_a, cargo_b = st.columns(2)
c1 = cargo_a.selectbox("Cargo A", sorted(df["cargo"].unique()))
c2 = cargo_b.selectbox("Cargo B", sorted(df["cargo"].unique()), index=1)

comp = (
    df_f[df_f["cargo"].isin([c1, c2])]
    .groupby("cargo")["salario"]
    .agg(media="mean", mediana="median")
    .reset_index()
)

fig = px.bar(
    comp,
    x="cargo",
    y=["media", "mediana"],
    barmode="group",
    title="Comparação salarial (média x mediana)",
    labels={"value": f"Salário ({moeda})", "variable": "Métrica"}
)

st.plotly_chart(fig, use_container_width=True)

delta = (comp.loc[1, "media"] / comp.loc[0, "media"] - 1) * 100
st.info(f"{c2} paga em média **{delta:.1f}%** a mais que {c1}")

# ===============================
# RANKING POR PAÍS (NOVO)
# ===============================
st.subheader("🌍 Países com maiores salários médios")

ranking = (
    df_f.groupby("residencia_iso3")["salario"]
    .mean()
    .nlargest(10)
    .reset_index()
)

fig = px.bar(
    ranking,
    x="salario",
    y="residencia_iso3",
    orientation="h",
    title="Top 10 países por salário médio",
    labels={"salario": f"Salário médio ({moeda})", "residencia_iso3": "País"}
)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# DOWNLOAD
# ===============================
st.download_button(
    "📥 Baixar dados filtrados",
    data=df_f.to_csv(index=False),
    file_name="salarios_filtrados.csv",
    mime="text/csv"
)

# ===============================
# TABELA
# ===============================
st.subheader("📋 Dados detalhados")
st.dataframe(df_f, use_container_width=True)

# ===============================
# SOBRE
# ===============================
with st.expander("ℹ️ Sobre este dashboard"):
    st.markdown("""
    • Visual orientado à decisão  
    • Moeda ajustável (USD / EUR)  
    • Gráficos explicativos e comparativos  
    • Projeto com foco corporativo e portfólio  
    """)
