import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import json
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build

st.title("🌱 Gestión de Pastoreo – Arriba y Pioneros")

# ================================
# Credenciales desde secrets
# ================================
raw = st.secrets["google"]["credentials_b64"]
decoded_json = base64.b64decode(raw).decode("utf-8")
creds_info = json.loads(decoded_json)

creds = service_account.Credentials.from_service_account_info(
    creds_info,
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)

service = build("drive", "v3", credentials=creds)

# ================================
# IDs de los archivos
# ================================
FILE_ID_ARRIBA = st.secrets["google"]["file_id_arriba"]
FILE_ID_PIONEROS = st.secrets["google"]["file_id_pioneros"]

# ================================
# Función para leer Excel
# ================================
@st.cache_data
def leer_excel_xlsx(file_id, sheet_name=0):
    request = service.files().get_media(fileId=file_id)
    file_bytes = request.execute()

    xls = pd.ExcelFile(BytesIO(file_bytes))
    df = pd.read_excel(xls, sheet_name=sheet_name)
    return df

# ================================
# Cargar ambos archivos
# ================================
df_arriba = leer_excel_xlsx(FILE_ID_ARRIBA, sheet_name=0)
df_pioneros = leer_excel_xlsx(FILE_ID_PIONEROS, sheet_name=0)

# ================================
# Identificar origen (MUY recomendado)
# ================================
df_arriba["FINCA"] = "ARRIBA"
df_pioneros["FINCA"] = "PIONEROS"
# Asegurar fecha
df_total["Fecha"] = pd.to_datetime(df_total["Fecha"])

# Crear periodo mensual
df_total["MES"] = df_total["Fecha"].dt.to_period("M")
# Filtrar por finca
df_finca = df_total[df_total["FINCA"] == finca_elegida]

# Mes actual y anterior
mes_actual = df_finca["MES"].max()
mes_anterior = mes_actual - 1

# Producción por mes
prod_actual = df_finca[df_finca["MES"] == mes_actual]["Pdcion"].sum()
prod_anterior = df_finca[df_finca["MES"] == mes_anterior]["Pdcion"].sum()
#---------columnas 
col1, col2, col3 = st.columns(3)

# ================================
# Unir si lo necesitas
# ================================
df_total = pd.concat([df_arriba, df_pioneros], ignore_index=True)
#---------Liampiar Datos
df_total["FINCA"] = (df_total["FINCA"].astype(str).str.strip().str.upper())
# Asegurar fecha
df_total["Fecha"] = pd.to_datetime(df_total["Fecha"])

# Crear periodo mensual
df_total["MES"] = df_total["Fecha"].dt.to_period("M")
# Filtrar por finca
df_finca = df_total[df_total["FINCA"] == finca_elegida]

# Mes actual y anterior
mes_actual = df_finca["MES"].max()
mes_anterior = mes_actual - 1

# Producción por mes
prod_actual = df_finca[df_finca["MES"] == mes_actual]["Pdcion"].sum()
prod_anterior = df_finca[df_finca["MES"] == mes_anterior]["Pdcion"].sum()
#---------columnas 
col1, col2, col3 = st.columns(3)
#------- dataframe promedio con selector
elegirfinca= st.selectbox("Seleccione una finca",df_total["FINCA"].unique())

promedioporfinca = (df_total.groupby(["Fecha", "FINCA"], as_index=False)["Pdcion"].mean())

tablafinca= promedioporfinca[
    promedioporfinca["FINCA"] == elegirfinca]
st.subheader(f"Promedio de producción – {elegirfinca}")
st.dataframe(tablafinca, use_container_width=True)

st.subheader(f"📈 KPI Producción – {finca_elegida}")

col1, col2, col3 = st.columns(3)

col1.metric(
    label="Producción mes actual",
    value=f"{prod_actual:,.0f} L"
)

col2.metric(
    label="Producción mes anterior",
    value=f"{prod_anterior:,.0f} L"
)
#------ Grafico1 



fig, ax = plt.subplots(figsize=(15,10))
sns.lineplot(data=df_total,x="Fecha",y="Pdcion",hue="FINCA", errorbar=None, marker="o")
ax.set_title("Aforo promedio por mes", fontsize=16)
plt.xticks(rotation=45)
ax.grid(True)

st.pyplot(fig)
st.write(df_total.columns)
