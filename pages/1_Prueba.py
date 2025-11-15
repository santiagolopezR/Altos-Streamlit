import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.title("🌱 Gestión de pastoreo – Altos de Medina")

# URLs de Google Sheets
url_produccion = "https://docs.google.com/spreadsheets/d/1zEiTqZ-9WnpwcpjV_LFRF9IcwHbqM04t/export?format=csv&gid=1070972783"
url_pastos = "https://docs.google.com/spreadsheets/d/1zEiTqZ-9WnpwcpjV_LFRF9IcwHbqM04t/export?format=csv&gid=392341065"


# Cargar datos
df = pd.read_csv(url_produccion)
dfpasto = pd.read_csv(url_pastos)

# -------------------------------
# LIMPIEZA (igual que tu código)
# -------------------------------

df.columns = df.columns.str.strip()
df["FINCA"] = df["FINCA"].str.strip().str.upper()
df = df[df["FINCA"] != "ABAJO"]
df["FECHA"] = pd.to_datetime(df["FECHA"])
df["LECHE TANQUE DIA"] = pd.to_numeric(df["LECHE TANQUE DIA"], errors='coerce')
df = df.dropna(subset=["LECHE TANQUE DIA"])

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
    .str.strip()
)

dfpasto["AFORO PLATOMETRO (Kg/m2)"] = pd.to_numeric(
    dfpasto["AFORO PLATOMETRO (Kg/m2)"], errors="coerce"
)
# Eliminar outliers mayores a 4
dfpasto = dfpasto[dfpasto["AFORO PLATOMETRO (Kg/m2)"] <= 4]
dfpasto = dfpasto.sort_values("FECHA")

# FILTRADO ELIMINAR LOTES 
df_filtrado = dfpasto[(dfpasto['FINCA'] == "ARRIBA") & (dfpasto['LOTE'].isin(["1", "2"]))]
dfpasto= dfpasto[~df_filtrado]




#------ grafica-----
fig, ax = plt.subplots(figsize=(15,10))
sns.lineplot(data=dfpasto, x="MES_ANO", y="AFORO PLATOMETRO (Kg/m2)", errorbar=None,hue="FINCA", ax=ax, marker="o")
ax.set_title("Aforo promedio mes")
plt.xticks(rotation=45)
ax.grid(True)
st.pyplot(fig)


#------ grafica ------
st.subheader("📊 Aforo por Lote")

# Seleccionar finca
finca_elegida = st.selectbox("Selecciona la finca", dfpasto["FINCA"].unique())
def grafica_aforo_por_finca(dfpasto, finca):
    

    # Filtrar finca
    data = dfpasto[dfpasto["FINCA"] == finca].copy()

    if data.empty:
        st.warning(f"No hay datos para la finca: {finca}")
        return

    # Crear figura
    fig, ax = plt.subplots(figsize=(15, 10))
    sns.lineplot(
        data=data,
        x="MES_ANO",
        y="AFORO PLATOMETRO (Kg/m2)",
        hue="LOTE",
        errorbar=None,
        marker="o",
        ax=ax
    )

    ax.set_title(f"Aforo promedio mes – {finca}", fontsize=16)
    plt.xticks(rotation=45)
    ax.grid(True)

    st.pyplot(fig)





# Llamar la función
grafica_aforo_por_finca(dfpasto, finca_elegida)