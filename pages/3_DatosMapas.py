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

# Pasar a WGS84 (obligatorio para mapas web)
gdf = gdf.to_crs(epsg=4326)

# Centro del mapa
lat = gdf.geometry.centroid.y.mean()
lon = gdf.geometry.centroid.x.mean()

# Crear mapa
m = folium.Map(location=[lat, lon], zoom_start=15)

# Agregar shapefile
folium.GeoJson(gdf).add_to(m)

# Mostrar en Streamlit
st_folium(m, width=800, height=500)
