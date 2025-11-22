import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import json
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build


# -----------------------------------------------------
# 1. CONFIGURACIÓN GOOGLE DRIVE API (USA TUS SECRETS)
# -----------------------------------------------------

creds_info = json.loads(st.secrets["google"]["credentials"])

# IDs del archivo (si son el mismo, puedes usar uno solo)
FILE_ID = st.secrets["google"]["file_id"]   # tu Google Sheet

# Crear credenciales del service account
creds = service_account.Credentials.from_service_account_info(
    creds_info,
    scopes=["https://www.googleapis.com/auth/drive"]
)

# Crear cliente Drive API
service = build("drive", "v3", credentials=creds)


# -----------------------------------------------------
# 2. FUNCIÓN PARA CARGAR EL EXCEL DESDE GOOGLE DRIVE API
# -----------------------------------------------------
def leer_hoja(file_id, gid):
    """
    Exporta la hoja indicada desde Google Sheets como Excel
    y la carga en un DataFrame de pandas.
    """
    request = service.files().export_media(
        fileId=file_id,
        mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    content = request.execute()

    xls = pd.ExcelFile(BytesIO(content))
    # Cada GID corresponde a una hoja pero Excel no usa GID.
    # Entonces cargamos por número de índice.
    return pd.read_excel(xls, sheet_name=0)  # hoja 1


# -----------------------------------------------------
# 3. LEER DATOS REMOTAMENTE (SIEMPRE ACTUALIZADOS)
# -----------------------------------------------------

# GIDs de tus hojas
GID_PRODUCCION = "1070972783"
GID_PASTOS = "392341065"

df = leer_hoja(FILE_ID, GID_PRODUCCION)
dfpasto = leer_hoja(FILE_ID, GID_PASTOS)


# -----------------------------------------------------
# 4. LIMPIEZA DE DATOS
# -----------------------------------------------------

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


# -----------------------------------------------------
# 5. INTERFAZ
# -----------------------------------------------------

st.title("📈 Producción de Leche – Altos de Medina")
st.sidebar.success("Seleccione una página 🤌.")


# -----------------------------------------------------
# 6. GRÁFICA GENERAL
# -----------------------------------------------------

st.subheader("📊 Producción de leche por día")
df["MES_ANO"] = df["FECHA"].dt.to_period("M").astype(str)

fig, ax = plt.subplots(figsize=(15, 5))
sns.lineplot(data=df, x="MES_ANO", y="LECHE TANQUE DIA", hue="FINCA", ax=ax, errorbar=None)
plt.xticks(rotation=45)
plt.title("LECHE TANQUE DIA")

st.pyplot(fig)


# -----------------------------------------------------
# 7. GRÁFICA ÚLTIMO MES
# -----------------------------------------------------

st.subheader("📊 Producción de leche – Último Mes")
df["MES"] = df["FECHA"].dt.to_period("M")

ultimo_mes = df["MES"].max()
df_ultimo_mes = df[df["MES"] == ultimo_mes]

fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.lineplot(data=df_ultimo_mes, x="FECHA", y="LECHE TANQUE DIA", hue="FINCA", ax=ax2)
plt.xticks(rotation=45)
plt.title("Producción Último Mes")

st.pyplot(fig2)


# -----------------------------------------------------
# 8. TABLA PIVOT
# -----------------------------------------------------

df["FECHA"] = df["FECHA"].dt.date
pivot = df.pivot_table(
    index='FECHA',
    columns='FINCA',
    values='LECHE TANQUE DIA',
    aggfunc='sum',
    fill_value=0
)
pivot["Suma Dia"] = pivot.sum(axis=1)

st.subheader("📋 Producción por finca")
st.dataframe(pivot.sort_index(ascending=False), use_container_width=True)


# -----------------------------------------------------
# 9. PROMEDIO POR VACA
# -----------------------------------------------------

df["promedio"] = df["LECHE TANQUE DIA"] / df["NUMERO VACAS ORDEÑO"]

fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.barplot(data=df, x="MES", y="promedio", hue="FINCA", ax=ax3, errorbar=None)
plt.xticks(rotation=50)
plt.title("Promedio por Finca")

st.pyplot(fig3)

