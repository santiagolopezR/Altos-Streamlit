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


# ================================
# Unir si lo necesitas
# ================================
df_total = pd.concat([df_arriba, df_pioneros], ignore_index=True)
#---------Liampiar Datos
df_total["FINCA"] = (df_total["FINCA"].astype(str).str.strip().str.upper())
#------- dataframe promedio con selector
elegirfinca= st.selectbox("Seleccione una finca",df_total["FINCA"].unique())

promedioporfinca= df_total.groupby("Fecha")["Pdcion"].mean()

def tablas_por_finca (df_total, finca):
    data= df_total[df_total["FINCA"]== finca]
    if data.empty:
        st.warning("No hay datos para esta finca.")
        return
    st.subheader(f"Datos {finca}")
    st.dataframe(promediofinca,use_container_width=True)
tablas_por_finca (df_total)

#------ Grafico1 



fig, ax = plt.subplots(figsize=(15,10))
sns.lineplot(data=df_total,x="Fecha",y="Pdcion",hue="FINCA", errorbar=None, marker="o")
ax.set_title("Aforo promedio por mes", fontsize=16)
plt.xticks(rotation=45)
ax.grid(True)

st.pyplot(fig)
st.subheader("📊 Datos Unificados")
st.dataframe(df_total.head(), use_container_width=True)
st.write(df_total["FINCA"].value_counts())
st.write(df_total.columns)
