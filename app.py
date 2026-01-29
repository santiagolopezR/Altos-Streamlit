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


# ================================
# 4. LIMPIEZA
# ================================

df.columns = df.columns.str.strip()
df["FINCA"] = df["FINCA"].str.strip().str.upper()
df = df[df["FINCA"] != "ABAJO"]

#------ fecha
# Convertir la columna a string y limpiar espacios
df["FECHA"] = df["FECHA"].astype(str).str.strip()

# Reemplazar valores vacíos o raros
df["FECHA"] = df["FECHA"].replace(["", " ", "nan", "NaN", None], pd.NA)

# Convertir definitivamente a datetime
df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)

# --- Crear columnas de tiempo ---
df["MES_ANO"] = df["FECHA"].dt.to_period("M").astype(str)
df["MES"] = df["FECHA"].dt.to_period("M")

df["LECHE TANQUE DIA"] = pd.to_numeric(df["LECHE TANQUE DIA"], errors="coerce")
df = df.dropna(subset=["LECHE TANQUE DIA"])


dfpasto["FINCA"] = dfpasto["FINCA"].astype(str).str.strip()
dfpasto = dfpasto[dfpasto["FINCA"] != "ABAJO"]
dfpasto["FECHA"] = pd.to_datetime(dfpasto["FECHA"], errors="coerce")
dfpasto = dfpasto.dropna(subset=["FECHA"])
dfpasto["LOTE"] = dfpasto["LOTE"].astype(str).str.strip()
dfpasto = dfpasto[~dfpasto["LOTE"].isin(["nan", "12", "10"])]


# ================================
# 5. INTERFAZ
# ================================
st.title("📈 Producción de Leche – Altos de Medina")
st.sidebar.success("Seleccione una página 🤌.")

# -----------------------------------------------------
# 6. GRÁFICA HISTÓRICA
# -----------------------------------------------------
st.subheader("📊 Producción de leche por día")

# Ordenar por fecha antes de graficar
df_sorted = df.sort_values(['FINCA', 'MES_ANO'])

fig = px.line(df_sorted, 
              x="MES_ANO", 
              y="LECHE TANQUE DIA", 
              color="FINCA", 
              line_dash="FINCA")

fig.update_xaxes(
    rangeslider_visible=True,
    tickangle=-45
)

fig.update_layout(height=600)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------
# 7. GRÁFICA ÚLTIMO MES
# -----------------------------------------------------

st.subheader("📊 Producción de leche – Último Mes")

ultimo_mes = df["MES"].max()
df_ultimo_mes = df[df["MES"] == ultimo_mes]

fig2 = px.line(df_ultimo_mes, 
               x="FECHA", 
               y="LECHE TANQUE DIA", 
               color="FINCA",
               markers=True,
               title="Producción Último Mes")

fig2.update_traces(marker=dict(size=8), line=dict(width=2.5))

fig2.update_layout(
    height=500,
    xaxis_title="Fecha",
    yaxis_title="Leche Tanque Día",
    xaxis_tickangle=-45
)

st.plotly_chart(fig2, use_container_width=True)


# -----------------------------------------------------
# 8. TABLA PIVOT
# -----------------------------------------------------
st.subheader("📋 Producción por finca")

# Crear copia para la tabla sin modificar el df original
df_tabla1 = df.copy()
df_tabla1["FECHA"] = df_tabla1["FECHA"].dt.date

pivot = df_tabla1.pivot_table(
    index='FECHA',
    columns='FINCA',
    values='LECHE TANQUE DIA',
    aggfunc='sum',
    fill_value=0
)
pivot["Suma Dia"] = pivot.sum(axis=1)

st.dataframe(pivot.sort_index(ascending=False), use_container_width=True)


# -----------------------------------------------------
# 9. PROMEDIO POR VACA
# -----------------------------------------------------
st.subheader("Promedio por finca 🐄")
df["promedio"] = df["LECHE TANQUE DIA"] / df["NUMERO VACAS ORDEÑO"]

df_plot = df.copy()
df_plot["MES"] = df_plot["MES"].astype(str)
df_plot["promedio"] = df_plot["promedio"].astype(float)

# Agrupar por MES y FINCA para obtener el promedio real
df_agrupado = df_plot.groupby(["MES", "FINCA"])["promedio"].mean().reset_index()

fig3 = px.line(df_agrupado, 
               x="MES", 
               y="promedio", 
               color="FINCA",
               markers=True,
               line_dash="FINCA",
               title="Promedio de Producción por Finca")

fig3.update_traces(marker=dict(size=10), line=dict(width=3))

fig3.update_layout(
    height=500,
    xaxis_tickangle=-90,
    xaxis_title="Mes",
    yaxis_title="Litros por Vaca"
)

st.plotly_chart(fig3, use_container_width=True)

#------ tabla promedio -----
st.subheader("📋 Tabla de promedios")

df_tabla2 = df.copy()
df_tabla2["FECHA"] = df_tabla2["FECHA"].dt.date
df_tabla2 = df_tabla2.drop_duplicates(subset=['FECHA', 'FINCA'], keep='first')

pivot2 = df_tabla2.pivot_table(
    index='FECHA',
    columns='FINCA',
    values='promedio',
    aggfunc='mean',
    fill_value=0
)

st.dataframe(pivot2.sort_index(ascending=False), use_container_width=True)


#----------- Grafico concentrado y relacion leche
st.subheader("Relacion Leche:Concentrado")
df_plot5 = df_plot[df_plot["RELACION LECHE CONCENTRADO"] <= 5]

#Agrupar por mes y finca
df_agrupado = df_plot5.groupby(["MES", "FINCA"])["RELACION LECHE CONCENTRADO"].mean().reset_index()

fig4 = px.line(df_agrupado, 
               x="MES", 
               y="RELACION LECHE CONCENTRADO",
               color="FINCA",
               markers=True,
               line_dash="FINCA",
               title="Relacion Leche:Concentrado por Finca")

fig4.update_traces(marker=dict(size=8), line=dict(width=2.5))
fig4.update_layout(height=500, xaxis_tickangle=-90)

st.plotly_chart(fig4, use_container_width=True)
st.write(df.columns)
