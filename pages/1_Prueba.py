import streamlit as st

st.title("Página de prueba")
st.write("Esta es la primera página creada desde GitHub.")

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

#-------- grafica-----
df["promedio"] = df["LECHE TANQUE DIA"]/df["NUMERO VACAS ORDEÑO"]
fig3, ax3 = plt.subplots(figsize=(10,5))
sns.barplot(data=df, x= "MES", y= "promedio", hue="FINCA",errorbar=None)
ax3.set_title("Promedio por Finca")
plt.xticks(rotation=50)
st.pyplot(fig3)