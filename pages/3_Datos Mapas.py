import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.title("Mapa de Potreros")

# Cargar shapefile
gdf = gpd.read_file("data/shp/pionerosPotreros.shp")

# Asegurar CRS para mapas web
if gdf.crs is not None and gdf.crs.to_string() != "EPSG:4326":
    gdf = gdf.to_crs(epsg=4326)

# Calcular centro del mapa (forma estable)
centro = gdf.geometry.representative_point()
lat = centro.y.mean()
lon = centro.x.mean()

# Crear mapa base
m = folium.Map(
    location=[lat, lon],
    zoom_start=15,
    tiles="OpenStreetMap"
)

# Agregar potreros (SIN tooltip para evitar errores)
folium.GeoJson(gdf).add_to(m)

# Mostrar en Streamlit
st_folium(m, width=1200, height=600)

