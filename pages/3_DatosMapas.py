import streamlit as st
import geopandas as gpd
from pathlib import Path
import folium
from streamlit_folium import st_folium

st.title("Mapa de Potreros")

# Ruta al shapefile
BASE_DIR = Path(__file__).resolve().parents[1]
shp_path = BASE_DIR / "data" / "shp" / "pionerosPotreros.shp"

# Cargar shapefile
gdf = gpd.read_file(shp_path)

# 👀 Verificar CRS
st.write("CRS original:", gdf.crs)

# ⚠️ SOLO si el CRS es None, asigna uno (ejemplo Colombia)
if gdf.crs is None:
    gdf = gdf.set_crs(epsg=3116)  # MAGNA-SIRGAS (ajustamos si hace falta)

# Convertir a WGS84
gdf = gdf.to_crs(epsg=4326)

# Centro del mapa
lat = gdf.geometry.centroid.y.mean()
lon = gdf.geometry.centroid.x.mean
