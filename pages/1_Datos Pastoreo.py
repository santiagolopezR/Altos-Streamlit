import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import base64
import json
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
import plotly.express as px

# ================================
# 1. Leer credenciales desde secrets
# ================================
raw = st.secrets["google"]["credentials_b64"]
decoded_json = base64.b64decode(raw).decode("utf-8")
creds_info = json.loads(decoded_json)

creds = service_account.Credentials.from_service_account_info(
    creds_info,
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)

# Cliente Drive API
service = build("drive", "v3", credentials=creds)

# ID del archivo Excel en Drive
FILE_ID = st.secrets["google"]["file_id"]


# ================================
# 2. Función para descargar el .xlsx
# ================================
def leer_excel_xlsx(file_id, sheet_name=0):
    """Descarga un archivo .xlsx de Drive y carga una hoja específica."""
    
    request = service.files().get_media(fileId=file_id)
    file_bytes = request.execute()

    xls = pd.ExcelFile(BytesIO(file_bytes))
    df = pd.read_excel(xls, sheet_name=sheet_name)

    return df


# ================================
# 3. Leer tus hojas (por índice)
# ================================

df = leer_excel_xlsx(FILE_ID, sheet_name=0)         # PRODUCCIÓN
dfpasto = leer_excel_xlsx(FILE_ID, sheet_name=4)    # PASTOS


# -------------------------------
# LIMPIEZA
# -------------------------------
dfpasto["FINCA"] = dfpasto["FINCA"].astype(str).str.strip()
dfpasto = dfpasto[dfpasto["FINCA"] != "ABAJO"]

dfpasto["FECHA"] = pd.to_datetime(dfpasto["FECHA"], errors="coerce")
dfpasto = dfpasto.dropna(subset=["FECHA"])

dfpasto["LOTE"] = dfpasto["LOTE"].astype(str).str.strip()
dfpasto = dfpasto[~dfpasto["LOTE"].isin(["nan", "12", "10"])]
#------ fecha
# Convertir la columna a string y limpiar espacios
dfpasto["FECHA"] = dfpasto["FECHA"].astype(str).str.strip()

# Reemplazar valores vacíos o raros
dfpasto["FECHA"] = dfpasto["FECHA"].replace(["", " ", "nan", "NaN", None], pd.NA)

# Convertir definitivamente a datetime
dfpasto["FECHA"] = pd.to_datetime(dfpasto["FECHA"], errors="coerce", dayfirst=True)
# --- Crear columna MES_AÑO ---
dfpasto["MES_ANO"] =dfpasto["FECHA"].dt.to_period("M").astype(str)

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

#Quitar lotes en las fincas
dfpasto = dfpasto[~(((dfpasto['FINCA'] == "ARRIBA") & (dfpasto['LOTE'].isin(["1", "2"]))) | ((dfpasto['FINCA'] == "LA POSADA") & (dfpasto['LOTE'].isin(["ALTA"]))))]
#fecha
dfpasto["FECHA"] = dfpasto["FECHA"].dt.date

## LIMPIAR COLUMNA CONSUMO (por si viene con comas, texto, etc.)
dfpasto["CONSUMO PASTO PLATOMETRO (Kg/vaca/día)"] = (
    dfpasto["CONSUMO PASTO PLATOMETRO (Kg/vaca/día)"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.strip()
)

dfpasto["CONSUMO PASTO PLATOMETRO (Kg/vaca/día)"] = pd.to_numeric(
    dfpasto["CONSUMO PASTO PLATOMETRO (Kg/vaca/día)"],
    errors="coerce"
)
# Fertilizantes
import re

# Normalizar texto
dfpasto["Fertilizacion"] = (
    dfpasto["Fertilizacion"]
    .astype(str)
    .str.upper()
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

# Unificaciones de nombres (correcciones reales)
dfpasto["Fertilizacion"] = dfpasto["Fertilizacion"].replace({
    "NIRAX": "NITRAX",
    "NIRAX ": "NITRAX",
    "NITRAX ": "NITRAX",
    " NITRAX": "NITRAX",
    "NITRAX  ": "NITRAX",
    "NITRAX  TIMAC": "NITRAX TIMAC",
    "NITRAX TIMAC ": "NITRAX TIMAC",
    "34-5-4 +KLESERITA": "34-5-4 + KLESERITA",
    "34-5-4 + KLESERITA ": "34-5-4 + KLESERITA",
    "COLANTA 34-5-4 ": "COLANTA 34-5-4",
})

# Quitar fertilizantes completamente vacíos
dfpasto = dfpasto[dfpasto["Fertilizacion"].str.strip() != ""]

# ---------------------------------------------------------------------------------------------
st.subheader("🎯 KPIs de Aforo - Mes Actual")

finca_kpi = st.selectbox("Selecciona finca:", dfpasto["FINCA"].unique(), key="kpi_aforo")

# Filtrar datos de la finca
data_finca = dfpasto[dfpasto["FINCA"] == finca_kpi].copy()
#asegurar que FECHA sea datetime
data_finca["FECHA"] = pd.to_datetime(data_finca["FECHA"], errors='coerce')

# Obtener mes actual y anterior
data_finca["MES"] = data_finca["FECHA"].dt.to_period("M")
mes_actual = data_finca["MES"].max()
mes_anterior = mes_actual - 1

# Datos del mes actual y anterior
datos_actual = data_finca[data_finca["MES"] == mes_actual]
datos_anterior = data_finca[data_finca["MES"] == mes_anterior]

# Calcular métricas
aforo_actual = datos_actual["AFORO PLATOMETRO (Kg/m2)"].mean()
aforo_anterior = datos_anterior["AFORO PLATOMETRO (Kg/m2)"].mean()
delta_aforo = aforo_actual - aforo_anterior if aforo_anterior > 0 else 0

consumo_actual = datos_actual["CONSUMO PASTO PLATOMETRO (Kg/vaca/día)"].mean()
consumo_anterior = datos_anterior["CONSUMO PASTO PLATOMETRO (Kg/vaca/día)"].mean()
delta_consumo = consumo_actual - consumo_anterior if consumo_anterior > 0 else 0

# Obtener el número de vacas más reciente del mes actual
vacas_totales = datos_actual["NUMERO VACAS LOTE"].iloc[-1] if len(datos_actual) > 0 else 0
num_lotes = datos_actual["LOTE"].nunique()

# Mostrar KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Aforo Promedio",
        value=f"{aforo_actual:.1f} Kg/m²",
        delta=f"{delta_aforo:.1f} Kg/m²"
    )

with col2:
    st.metric(
        label="🐄 Consumo Promedio",
        value=f"{consumo_actual:.1f} Kg/vaca",
        delta=f"{delta_consumo:.1f} Kg/vaca"
    )

with col3:
    st.metric(
        label="🐮 Total Vacas",
        value=f"{vacas_totales:.0f}",
        delta=None
    )

with col4:
    st.metric(
        label="🌱 Lotes Activos",
        value=f"{num_lotes}",
        delta=None
    )





# GRAFICA GENERAL

st.subheader("📊 Aforo Promedio por Mes – General")

# Preparar datos
dfpasto_plot = dfpasto.copy()

# Ordenar por fecha
dfpasto_plot = dfpasto_plot.sort_values(['FINCA', 'MES_ANO'])
#AGRUPAR por mes y finca (promedio mensual)
dfpasto_agrupado = dfpasto_plot.groupby(["MES_ANO", "FINCA"])["AFORO PLATOMETRO (Kg/m2)"].mean().reset_index()

# Ordenar
dfpasto_agrupado = dfpasto_agrupado.sort_values(['FINCA', 'MES_ANO'])
fig = px.line(dfpasto_agrupado,
              x="MES_ANO",
              y="AFORO PLATOMETRO (Kg/m2)",
              color="FINCA",
              markers=True,
              line_dash="FINCA",
              title="Aforo promedio por mes")

fig.update_traces(marker=dict(size=8), line=dict(width=2.5))

fig.update_layout(
    height=600,
    width=5000,
    xaxis_tickangle=-45,
    xaxis_title="Mes/Año",
    yaxis_title="Aforo Platómetro (Kg/m²)",
    showlegend=True
)

fig.update_xaxes(showgrid=True)
fig.update_yaxes(showgrid=True)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# GRAFICA POR FINCA
# -------------------------------
st.subheader("📈 AFORO por Lote – Finca específica")

finca_elegida = st.selectbox(
    "Selecciona una finca",
    dfpasto["FINCA"].unique(),
    key="finca_aforo"
)


def grafica_aforo_por_finca(dfpasto, finca):
    data = dfpasto[dfpasto["FINCA"] == finca].copy()
    
    if data.empty:
        st.warning("No hay datos para esta finca.")
        return
    
    # Convertir MES_ANO a string si es Period
    data["MES_ANO"] = data["MES_ANO"].astype(str)
    
    # Ordenar por fecha
    data = data.sort_values(["LOTE", "MES_ANO"])
    
    fig = px.line(data,
                  x="MES_ANO",
                  y="AFORO PLATOMETRO (Kg/m2)",
                  color="LOTE",
                  markers=True,
                  line_dash="LOTE",
                  title=f"Aforo promedio mes – {finca}")
    
    fig.update_traces(marker=dict(size=8), line=dict(width=2.5))
    
    fig.update_layout(
        height=600,
        xaxis_tickangle=-45,
        xaxis_title="Mes/Año",
        yaxis_title="Aforo Platómetro (Kg/m²)"
    )
    
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)
    
    st.plotly_chart(fig, use_container_width=True)

# Llamar la función
grafica_aforo_por_finca(dfpasto, finca_elegida)


#------ tabla

pivot3 = dfpasto.pivot_table(
    index='FECHA',
    columns='FINCA',
    values='AFORO PLATOMETRO (Kg/m2)',
    aggfunc='mean',
    fill_value=0)
st.dataframe(pivot3.sort_index(ascending=False), use_container_width=True)


# ------------------------------- Consumo por finca lote
st.subheader("📈 CONSUMO KG/VACA/DIA por Lote – Finca específica")
finca_elegida2 = st.selectbox(
    "Selecciona una finca",
    dfpasto["FINCA"].unique(),
    key="finca_consumo")

def grafica_consumo_por_finca(dfpasto, finca):
    data = dfpasto[dfpasto["FINCA"] == finca].copy()
    
    if data.empty:
        st.warning("No hay datos para esta finca.")
        return
    
    # Convertir MES_ANO a string
    data["MES_ANO"] = data["MES_ANO"].astype(str)
    
    # Agrupar por mes y lote (promedio mensual)
    data_agrupado = data.groupby(["MES_ANO", "LOTE"])["CONSUMO PASTO PLATOMETRO (Kg/vaca/día)"].mean().reset_index()
    
    # Ordenar
    data_agrupado = data_agrupado.sort_values(["LOTE", "MES_ANO"])
    
    # Crear gráfica con seaborn
    fig, ax = plt.subplots(figsize=(15, 6))
    
    sns.lineplot(
        data=data_agrupado,
        x="MES_ANO",
        y="CONSUMO PASTO PLATOMETRO (Kg/vaca/día)",
        hue="LOTE",
        marker="o",
        ax=ax
    )
    
    ax.set_title(f"Consumo promedio mes – {finca}", fontsize=16)
    ax.set_xlabel("Mes/Año", fontsize=12)
    ax.set_ylabel("CONSUMO PASTO PLATOMETRO (Kg/vaca/día)", fontsize=12)
    plt.xticks(rotation=45)
    ax.grid(True)
    plt.tight_layout()
    
    st.pyplot(fig)

grafica_consumo_por_finca(dfpasto, finca_elegida2)
#------ Tabla

st.subheader("Consumo promedio por Finca")

pivot4 = dfpasto.pivot_table(
    index='FECHA',
    columns=['FINCA', 'LOTE'],   # ← coma al final
    values='CONSUMO PASTO PLATOMETRO (Kg/vaca/día)',
    aggfunc='mean',
    fill_value=0
)

st.dataframe(
    pivot4.sort_index(ascending=False),
    use_container_width=True
)


#------- Tabla

st.subheader("Aforo promedio por Finca")

pivot5= dfpasto.pivot_table(
    index= "FECHA",
    columns=["FINCA","LOTE"],
    values="AFORO PLATOMETRO (Kg/m2)",
    aggfunc="mean",
    fill_value=0
)
st.dataframe(
    pivot5.sort_index(ascending=False),
    use_container_width=True
)
#-------------------- Tabla aforos total
st.subheader("Datos Aforos Completos")

st.dataframe(
    dfpasto.sort_values("FECHA", ascending=False),
    use_container_width=True
)
#--------- Tabla Abonos
tabla_group = (
    dfpasto.groupby(["FINCA", "Fertilizacion"], as_index=False)
           .agg({"AFORO PLATOMETRO (Kg/m2)": "mean"})
           .rename(columns={"AFORO PLATOMETRO (Kg/m2)": "Aforo_Promedio"})
)

st.subheader("📊 Aforo promedio por FINCA y FERTILIZACIÓN")
st.dataframe(tabla_group, use_container_width=True)

