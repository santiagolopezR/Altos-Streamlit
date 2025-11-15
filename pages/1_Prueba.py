grupi=dfpasto.groupby(["FECHA"])["AFORO PLATOMETRO (Kg/m2)"].mean()
st.table(grupi)