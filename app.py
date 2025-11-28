import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import base64
import json
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build


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

# 1. Convertir a string para evitar errores de tipos mezclados
df["FECHA"] = df["FECHA"].astype(str)

# 2. Convertir a fecha, ignorando errores
df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)

# 3. Ahora sí usar .dt.date
df["FECHA"] = df["FECHA"].dt.date

df["LECHE TANQUE DIA"] = pd.to_numeric(df["LECHE TANQUE DIA"], errors="coerce")
df = df.dropna(subset=["LECHE TANQUE DIA"])


dfpasto["FINCA"] = dfpasto["FINCA"].astype(str).str.strip()
dfpasto = dfpasto[dfpasto["FINCA"] != "ABAJO"]
dfpasto["FECHA"] = pd.to_datetime(dfpasto["FECHA"], errors="coerce")
dfpasto = dfpasto.dropna(subset=["FECHA"])
dfpasto["LOTE"] = dfpasto["LOTE"].astype(str).str.strip()
dfpasto = dfpasto[~dfpasto["LOTE"].isin(["nan", "12", "10"])]


# ================================
# 5. GRÁFICAS / INTERFAZ
# ================================
st.title("📈 Producción de Leche – Altos de Medina")

st.subheader("📊 Producción de leche por día")
df["MES_ANO"] = df["FECHA"].dt.to_period("M").astype(str)

fig, ax = plt.subplots(figsize=(15, 5))
sns.lineplot(data=df, x="MES_ANO", y="LECHE TANQUE DIA", hue="FINCA", ax=ax, errorbar=None,marker="o")
plt.xticks(rotation=45)
st.pyplot(fig)


# -----------------------------------------------------
# 5. INTERFAZ
# -----------------------------------------------------

st.title("📈 Producción de Leche – Altos de Medina")
st.sidebar.success("Seleccione una página 🤌.")


# -----------------------------------------------------
# 7. GRÁFICA ÚLTIMO MES
# -----------------------------------------------------

st.subheader("📊 Producción de leche – Último Mes")
df["MES"] = df["FECHA"].dt.to_period("M")

ultimo_mes = df["MES"].max()
df_ultimo_mes = df[df["MES"] == ultimo_mes]

fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.lineplot(data=df_ultimo_mes, x="FECHA", y="LECHE TANQUE DIA", hue="FINCA", ax=ax2, marker="o",)
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



st.subheader("Promedio por finca 🐄")
df["promedio"] = df["LECHE TANQUE DIA"] / df["NUMERO VACAS ORDEÑO"]

fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.barplot(data=df, x="MES", y="promedio", hue="FINCA", ax=ax3, errorbar=None)
plt.xticks(rotation=50)
plt.title("Promedio por Finca")

st.pyplot(fig3)

#------ tabla promedio-----
pivot2 = df.pivot_table(
    index='FECHA',
    columns='FINCA',
    values='promedio',
    aggfunc='sum',
    fill_value=0)
st.dataframe(pivot2.sort_index(ascending=False), use_container_width=True)

