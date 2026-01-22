import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.title("Mapa de Potreros")

# Cargar shapefile
gdf = gpd.read_file("data/shp/pionerosPotreros.shp")

# Mostrar CRS (debug)
st.write("CRS:", gdf.crs)

# Asegurar WGS84
if gdf.crs is None:
    st.error("El shapefile no tiene CRS definido")
else:
    if gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)

# Centro del mapa (forma segura)
centro = gdf.geometry.representative_point()
lat = centro.y.mean()
lon = centro.x.mean()

# Crear mapa
m = folium.Map(
    location=[lat, lon],
    zoom_start=15,
    tiles="OpenStreetMap"
)

# Agregar potreros
folium.GeoJson(
    gdf,
    tooltip=folium.GeoJsonTooltip(fields=list(gdf.columns))
).add_to(m)

# Mostrar mapa
st_folium(m, width=1200, height=600)

