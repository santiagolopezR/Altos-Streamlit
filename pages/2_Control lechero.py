girimport streamlit as st
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
# Asegurar fecha

#------- dataframe promedio con selector
elegirfinca= st.selectbox("Seleccione una finca",df_total["FINCA"].unique())

promedioporfinca = (df_total.groupby(["Fecha", "FINCA"], as_index=False)["Pdcion"].mean())

tablafinca= promedioporfinca[
    promedioporfinca["FINCA"] == elegirfinca]
st.subheader(f"Promedio de producción – {elegirfinca}")
st.dataframe(tablafinca, use_container_width=True)
df_total["Fecha"] = pd.to_datetime(df_total["Fecha"])


#------ Grafico1 

columnas_numericas = [
    col for col in df_total.columns
    if df_total[col].dtype in ["int64", "float64"]
]

columna_elegida = st.selectbox(
    "Seleccione la variable a analizar",
    columnas_numericas,
    index=columnas_numericas.index("Pdcion") if "Pdcion" in columnas_numericas else 0
)

# ======================================
# FILTRAR FINCA
# ======================================

df_finca = df_total[df_total["FINCA"] == finca_elegida].copy()

# ======================================
# KPI MES ACTUAL VS ANTERIOR
# ======================================

df_finca["MES"] = df_finca["Fecha"].dt.to_period("M")

resumen_mes = (
    df_finca.groupby("MES")[columna_elegida]
    .mean()
    .sort_index()
)

if len(resumen_mes) >= 2:
    mes_actual = resumen_mes.iloc[-1]
    mes_anterior = resumen_mes.iloc[-2]
    delta = mes_actual - mes_anterior
else:
    mes_actual = resumen_mes.iloc[-1]
    mes_anterior = None
    delta = None

col1, col2, col3 = st.columns(3)

col1.metric(
    "Mes actual",
    round(mes_actual, 2)
)

if mes_anterior is not None:
    col2.metric(
        "Mes anterior",
        round(mes_anterior, 2)
    )
    col3.metric(
        "Variación",
        round(delta, 2),
        delta=round(delta, 2)
    )
else:
    col2.metric("Mes anterior", "N/A")
    col3.metric("Variación", "N/A")

# ======================================
# FUNCIÓN GRÁFICA DE BARRAS
# ======================================

def grafica_barras(df, x_col, y_col, titulo, hue_col=None):
    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(
        data=df,
        x=x_col,
        y=y_col,
        hue=hue_col,
        errorbar=None,
        ax=ax
    )

    ax.set_title(titulo)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.grid(axis="y")
    plt.xticks(rotation=45)

    st.pyplot(fig)

# ======================================
# GRÁFICA POR MES
# ======================================

df_mes = (
    df_finca
    .groupby("MES", as_index=False)[columna_elegida]
    .mean()
)

grafica_barras(
    df=df_mes,
    x_col="MES",
    y_col=columna_elegida,
    titulo=f"{columna_elegida} promedio mensual – {finca_elegida}"
)

# ======================================
# TABLA RESUMEN
# ======================================

st.subheader(f"📋 Resumen mensual – {finca_elegida}")

st.dataframe(
    df_mes.sort_values("MES", ascending=False),
    use_container_width=True)
