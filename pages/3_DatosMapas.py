import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.title("Mapa de Potreros")

gdf = gpd.read_file("data/shp/pionerosPotreros.shp")

# Asegurar CRS web
gdf = gdf.to_crs(epsg=4326)

# Centro del mapa
centro = gdf.geometry.unary_union.centroid

m = folium.Map(
    location=[centro.y, centro.x],
    zoom_start=15
)

folium.GeoJson(gdf).add_to(m)

st_folium(m, width=1200, height=600)
