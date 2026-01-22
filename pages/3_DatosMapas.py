import streamlit as st
import geopandas as gpd
from pathlib import Path
import folium
from streamlit_folium import st_folium

st.title("Mapa de Potreros")

BASE_DIR = Path(__file__).resolve().parents[1]
shp_path = BASE_DIR / "data" / "shp" / "pionerosPotreros.shp"

gdf = gpd.read_file(shp_path)

st.write("CRS:", gdf.crs)

lat = gdf.geometry.centroid.y.mean()
lon = gdf.geometry.centroid.x.mean()

m = folium.Map(location=[lat, lon], zoom_start=15)

# 🔑 CLAVE: usar geo_interface
folium.GeoJson(gdf.__geo_interface__).add_to(m)

st_folium(m, width=900, height=550, key="mapa_potreros")
obligatoria
st_folium(m, width=900, height=550, key="mapa_potreros")
