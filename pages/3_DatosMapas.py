import streamlit as st
import geopandas as gpd
from pathlib import Path
import folium
from streamlit_folium import st_folium

st.title("Mapa de Potreros")

BASE_DIR = Path(__file__).resolve().parents[1]
shp_path = BASE_DIR / "data" / "shp" / "pionerosPotreros.shp"

gdf = gpd.read_file(shp_path)

# 👉 ASIGNAR CRS ORIGINAL (CAMBIA EPSG SI ES NECESARIO)
gdf = gdf.set_crs(epsg=3116)   # <-- prueba con 3116 o dime cuál usa

# 👉 CONVERTIR A WGS84
gdf = gdf.to_crs(epsg=4326)

# Centro del mapa
lat = gdf.geometry.centroid.y.mean()
lon = gdf.geometry.centroid.x.mean()

# Mapa
m = folium.Map(location=[lat, lon], zoom_start=15)

folium.GeoJson(gdf).add_to(m)

st_folium(m, width=800, height=500)
