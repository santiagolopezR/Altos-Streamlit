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
dfpasto = leer_excel_xlsx(FILE_ID, sheet_name=1)    # PASTOS


# ================================
# 4. LIMPIEZA
# ================================

df.columns = df.columns.str.strip()
df["FINCA"] = df["FINCA"].str.strip().str.upper()
df = df[df["FINCA"] != "ABAJO"]

df["FECHA"] = pd.to_datetime(df["FECHA"])
df["LECHE TANQUE DIA"] = pd.to_numeric(df["LECHE TANQUE DIA"], errors="coerce")
df = df.dropna(subset=["LECHE TANQUE DIA"])


#dfpasto["FINCA"] = dfpasto["FINCA"].astype(str).str.strip()
#dfpasto = dfpasto[dfpasto["FINCA"] != "ABAJO"]
#dfpasto["FECHA"] = pd.to_datetime(dfpasto["FECHA"], errors="coerce")
#dfpasto = dfpasto.dropna(subset=["FECHA"])
#dfpasto["LOTE"] = dfpasto["LOTE"].astype(str).str.strip()
#dfpasto = dfpasto[~dfpasto["LOTE"].isin(["nan", "12", "10"])]


# ================================
# 5. GRÁFICAS / INTERFAZ
# ================================
st.title("📈 Producción de Leche – Altos de Medina")

st.subheader("📊 Producción de leche por día")
df["MES_ANO"] = df["FECHA"].dt.to_period("M").astype(str)

fig, ax = plt.subplots(figsize=(15, 5))
sns.lineplot(data=df, x="MES_ANO", y="LECHE TANQUE DIA", hue="FINCA", ax=ax, errorbar=None)
plt.xticks(rotation=45)
st.pyplot(fig)