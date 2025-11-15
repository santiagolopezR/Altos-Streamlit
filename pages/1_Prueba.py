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
dfpasto['AFORO PLATOMETRO (Kg/m2)']= dfpasto['AFORO PLATOMETRO (Kg/m2)'].astype(str).str.replace(",",".")
#------ grafica-----
fig, ax = plt.subplots(figsize=(15,10))
sns.barplot(data=dfpasto, x="MES_ANO", y="AFORO PLATOMETRO (Kg/m2)", hue="FINCA", ax=ax)
ax.set_title("Aforo promedio mes")
plt.xticks(rotation=45)
st.pyplot(fig)


# Muestra los primeros 10 valores de la columna que estás graficando
st.write("Verificando los valores que recibe la gráfica (Primeros 10):")
st.dataframe(dfpasto.head(10)[['AFORO PLATOMETRO (Kg/m2)', 'MES_ANO']])

# Si los valores mostrados son negativos, el error está en la limpieza/agregación.
#------ Codigo de la gráfica SIN MARGEN EN EL EJE Y -----

# 1. Calcular el valor máximo, sin multiplicar por 1.1
y_max = dfpasto['AFORO PLATOMETRO (Kg/m2)'].max()

fig, ax = plt.subplots(figsize=(15,10))

# Dibujamos el gráfico de barras
sns.barplot(data=dfpasto, x="MES_ANO", y="AFORO PLATOMETRO (Kg/m2)", hue="FINCA", ax=ax)

# 2. LÍNEA CRÍTICA: Forzar el rango del eje Y de 0 al valor máximo.
# El borde superior de la barra más alta tocará el borde superior del gráfico.
ax.set_ylim(0, y_max) 

ax.set_title("Aforo promedio mes")
plt.xticks(rotation=45)
st.pyplot(fig)
