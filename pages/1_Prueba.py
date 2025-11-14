# 📊 Producción de Leche - Altos de Medina

import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

from app import cargar_datos_produccion

# ---- Cargar datos ----
df = cargar_datos_produccion()

st.title("📊 Producción de Leche - Altos de Medina")
st.write("Datos actualizados automáticamente desde Google Sheets cada 12 horas.")

# ---- Mostrar tabla ----
st.subheader("Tabla de datos")
st.dataframe(df)

# ---- Gráfica ----
st.subheader("Gráfica de producción diaria")

fig, ax = plt.subplots(figsize=(10,4))
sns.lineplot(
    data=df,
    x="FECHA",
    y="LECHE TANQUE DIA",
    hue="FINCA",
    ax=ax
)
ax.set_title("Producción diaria de leche")
ax.set_xlabel("Fecha")
ax.set_ylabel("Litros")
ax.grid(True)

st.pyplot(fig)