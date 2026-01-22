import streamlit as st
import geopandas as gpd

st.title("Mapa de Potreros (simple)")

gdf = gpd.read_file("data/shp/pionerosPotreros.shp")

# Asegurar CRS
gdf = gdf.to_crs(epsg=4326)

# Convertir polígonos a puntos
gdf["lat"] = gdf.geometry.centroid.y
gdf["lon"] = gdf.geometry.centroid.x

# Mostrar mapa
st.map(gdf[["lat", "lon"]])
