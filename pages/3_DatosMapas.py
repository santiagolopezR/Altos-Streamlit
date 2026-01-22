import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🌱 Mapa de Potreros – Pioneros")

# === Cargar SHP ===
gdf = gpd.read_file("data/shp/pionerosPotreros.shp")

# === Asegurar CRS correcto ===
if gdf.crs is None:
    gdf.set_crs(epsg=4326, inplace=True)
else:
    gdf = gdf.to_crs(epsg=4326)

# === Centro del mapa ===
centro = gdf.geometry.unary_union.centroid
m = folium.Map(
    location=[centro.y, centro.x],
    zoom_start=15,
    tiles="OpenStreetMap"
)

# === Agregar potreros ===
folium.GeoJson(
    gdf,
    name="Potreros",
    tooltip=folium.GeoJsonTooltip(
        fields=gdf.columns.
