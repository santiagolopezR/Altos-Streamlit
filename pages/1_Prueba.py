import streamlit as st
import pandas as pd
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
#------ grafica-----
fig, ax = plt.subplots(figsize=(15,10))
sns.barplot(data=dfpasto, x="MES_ANO", y="AFORO PLATOMETRO (Kg/m2)", hue="FINCA")
st.pyplot(fig)