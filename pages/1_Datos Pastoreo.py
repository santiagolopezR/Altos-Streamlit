import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("🌱 Gestión de Pastoreo – Altos de Medina")

# -------------------------------
# Cargar datos llamando funciones del app principal
# -------------------------------
@st.cache_data
def load_dfpasto():
    url_pastos = "https://docs.google.com/spreadsheets/d/1zEiTqZ-9WnpwcpjV_LFRF9IcwHbqM04t/export?format=csv&gid=392341065"
    dfpasto = pd.read_csv(url_pastos)
    return dfpasto

dfpasto = load_dfpasto()

# -------------------------------
# LIMPIEZA
# -------------------------------
dfpasto["FINCA"] = dfpasto["FINCA"].astype(str).str.strip()
dfpasto = dfpasto[dfpasto["FINCA"] != "ABAJO"]

dfpasto["FECHA"] = pd.to_datetime(dfpasto["FECHA"], errors="coerce")
dfpasto = dfpasto.dropna(subset=["FECHA"])

dfpasto["LOTE"] = dfpasto["LOTE"].astype(str).str.strip()
dfpasto = dfpasto[~dfpasto["LOTE"].isin(["nan", "12", "10"])]

dfpasto["MES_ANO"] = dfpasto["FECHA"].dt.to_period("M").astype(str)

dfpasto["AFORO PLATOMETRO (Kg/m2)"] = (
    dfpasto["AFORO PLATOMETRO (Kg/m2)"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)
dfpasto["AFORO PLATOMETRO (Kg/m2)"] = pd.to_numeric(
    dfpasto["AFORO PLATOMETRO (Kg/m2)"],
    errors="coerce"
)

# Eliminar outliers mayores a 4
dfpasto = dfpasto[dfpasto["AFORO PLATOMETRO (Kg/m2)"] <= 4]

# Ordenar por fecha
dfpasto = dfpasto.sort_values("FECHA")

# -------------------------------
# GRAFICA GENERAL
# -------------------------------
st.subheader("📊 Aforo Promedio por Mes – General")

fig, ax = plt.subplots(figsize=(15, 10))
sns.lineplot(
    data=dfpasto,
    x="MES_ANO",
    y="AFORO PLATOMETRO (Kg/m2)",
    hue="FINCA",
    marker="o",
    errorbar=None,
    ax=ax
)
ax.set_title("Aforo promedio por mes", fontsize=16)
plt.xticks(rotation=45)
ax.grid(True)

st.pyplot(fig)

# -------------------------------
# GRAFICA POR FINCA
# -------------------------------
st.subheader("📈 Aforo por Lote – Finca específica")

finca_elegida = st.selectbox("Selecciona una finca", dfpasto["FINCA"].unique())


def grafica_aforo_por_finca(dfpasto, finca):
    data = dfpasto[dfpasto["FINCA"] == finca]

    if data.empty:
        st.warning("No hay datos para esta finca.")
        return

    fig, ax = plt.subplots(figsize=(15, 10))
    sns.lineplot(
        data=data,
        x="MES_ANO",
        y="AFORO PLATOMETRO (Kg/m2)",
        hue="LOTE",
        marker="o",
        errorbar=None,
        ax=ax
    )

    ax.set_title(f"Aforo promedio mes – {finca}", fontsize=16)
    plt.xticks(rotation=45)
    ax.grid(True)

    st.pyplot(fig)


grafica_aforo_por_finca(dfpasto, finca_elegida)