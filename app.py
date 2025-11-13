
import streamlit as st
import pandas as pd

st.title("📊 Producción de Leche - Altos de Medina")

# Cargar datos de Excel
file_path = "Registro_Produccion_Dia.xlsx"
df = pd.read_excel(file_path)

# Mostrar una vista de la tabla
st.subheader("Datos de producción")
st.dataframe(df.head())

# Mostrar resumen
st.subheader("Resumen estadístico")
st.write(df.describe())
