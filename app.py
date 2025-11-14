
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("📈 Producción de Leche – Altos de Medina")

# URLs de Google Sheets
url_produccion = "https://docs.google.com/spreadsheets/d/1zEiTqZ-9WnpwcpjV_LFRF9IcwHbqM04t/export?format=csv&gid=1070972783"
url_pastos = "https://docs.google.com/spreadsheets/d/1zEiTqZ-9WnpwcpjV_LFRF9IcwHbqM04t/export?format=csv&gid=392341065"

st_autorefresh(interval=6000000)  # se actualiza cada 60 segundos
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

# -------------------------------
# (IQR eliminado según tu petición)
# -------------------------------

# -------------------------------
# GRAFICA
# -------------------------------
st.subheader("📊 Producción de leche por día")
df["MES_ANO"] = df["FECHA"].dt.to_period("M").astype(str)
fig, ax = plt.subplots(figsize=(15,5))
sns.lineplot(data=df, x="MES_ANO", y="LECHE TANQUE DIA", hue="FINCA", ax=ax, errorbar=None)
plt.xticks(rotation=45)
plt.title("LECHE TANQUE DIA")


st.pyplot(fig)

# -------------------------------
# GRAFICA
# -------------------------------
st.subheader("📊 Producción de leche por día (último mes)")
df['FECHA'] = pd.to_datetime(df['FECHA'])
df['MES'] = df['FECHA'].dt.to_period('M')

# Filtrar los datos del último mes
ultimo_mes = df['MES'].max()
df_ultimo_mes = df[df['MES'] == ultimo_mes]

# Graficar la leche tanque día para el último mes
fig2, ax2 = plt.subplots(figsize=(10,5))
sns.lineplot(data=df_ultimo_mes, x="FECHA", y="LECHE TANQUE DIA", hue="FINCA", ax=ax2)
plt.setp(ax2.get_xticklabels(), rotation=45)
ax2.set_title("LECHE TANQUE DIA - Último Mes")
ax2.set_xlabel("FECHA")
ax2.set_ylabel("LECHE TANQUE DIA")
ax2.grid(True)

st.pyplot(fig2)

#--------------------------- tabla -----------------
df['FECHA'] = df['FECHA'].dt.date
# Cambia aggfunc a 'sum' o 'mean' según lo que quieras mostrar
pivot = df.pivot_table(index='FECHA', columns='FINCA', values='LECHE TANQUE DIA', aggfunc='sum', fill_value=0)
pivot['Suma Dia'] = pivot.sum(axis=1)
st.subheader(f"Producción por finca")
st.dataframe(pivot.sort_index(ascending=False), use_container_width=True)

