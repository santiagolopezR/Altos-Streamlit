import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("📈 Producción de Leche – Altos de Medina")

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

df["LECHE TANQUE DIA"] = pd.to_numeric(df["LECHE TANQUE DIA"], errors='coerce')
df = df.dropna(subset=["LECHE TANQUE DIA"])

dfpasto["FINCA"] = dfpasto["FINCA"].astype(str).str.strip()
dfpasto = dfpasto[dfpasto["FINCA"] != "ABAJO"]

dfpasto["FECHA"] = pd.to_datetime(dfpasto["FECHA"], errors="coerce")
dfpasto = dfpasto.dropna(subset=["FECHA"])
dfpasto["LOTE"] = dfpasto["LOTE"].astype(str).str.strip()
dfpasto = dfpasto[~dfpasto["LOTE"].isin(["nan", "12", "10"])]

# IQR para eliminar outliers del aforo
Q1 = dfpasto["AFORO PLATOMETRO (Kg/m2)"].quantile(0.25)
Q3 = dfpasto["AFORO PLATOMETRO (Kg/m2)"].quantile(0.75)
IQR = Q3 - Q1
limite_inf = Q1 - 1.5 * IQR
limite_sup = Q3 + 1.5 * IQR
dfpasto = dfpasto[(dfpasto["AFORO PLATOMETRO (Kg/m2)"] >= limite_inf) &
                  (dfpasto["AFORO PLATOMETRO (Kg/m2)"] <= limite_sup)]

# -------------------------------
# GRAFICA
# -------------------------------
st.subheader("📊 Producción de leche por día")

fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="FECHA", y="LECHE TANQUE DIA", hue="FINCA", ax=ax)
plt.xticks(rotation=45)
plt.title("LECHE TANQUE DIA")
plt.grid(True)

st.pyplot(fig)
