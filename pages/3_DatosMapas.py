import streamlit as st
import geopandas as gpd
from pathlib import Path
import folium
from streamlit_folium import st_folium

st.title("Mapa de Potreros")

BASE_DIR = Path(__file__).resolve().parents[1]
shp_path = BASE_DIR / "data" / "shp" / "pionerosPotreros.shp"

# Cargar
gdf = gpd.read_file(shp_path)

# Confirmar CRS
st.write("CRS:", gdf.crs)

# 👉 LIMPIEZA CRÍTICA
gdf = gdf[gdf.geometry.notnull()]          # quitar geometrías nulas
gdf = gdf[gdf.is_valid]                    # quitar inválidas
gdf["geometry"] = gdf.geometry.buffer(0)  # arreglar geometrías

st.write("Geometrías válidas:", len(gdf))

# Centro seguro
centro = gdf.geometry.representative_point()
lat = centro.y.mean()
lon = centro.x.mean()

# Mapa
m = folium.Map(location=[lat, lon], zoom_start=14)

# 👉 PASAR A GEOJSON LIMPIO
folium.GeoJson(
    gdf.to_json(),
    name="potreros"
).add_to(m)

st_folium(m, width=900, height=550, key="mapa_potreros")
