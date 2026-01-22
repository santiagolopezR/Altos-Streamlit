import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.title("Mapa de Potreros")

# Cargar shapefile
gdf = gpd.read_file("data/shp/pionerosPotreros.shp")

# Asegurar CRS para web
if gdf.crs is not None and gdf.crs.to_string() != "EPSG:4326":
    gdf = gdf.to_crs(epsg=4326)

# =========================
# CALCULAR ÁREA CON GEOPANDAS
# =========================
# Usar CRS métrico para áreas
gdf_m = gdf.to_crs(epsg=3857)

# Área en hectáreas
gdf["area_ha"] = (gdf_m.geometry.area / 10_000).round(2)

# =========================
# CENTRO DEL MAPA
# =========================
centro = gdf.geometry.representative_point()
lat = centro.y.mean()
lon = centro.x.mean()

# Crear mapa
m = folium.Map(
    location=[lat, lon],
    zoom_start=15,
    tiles="OpenStreetMap"
)

# =========================
# POTREROS CON NOMBRE Y ÁREA
# =========================
folium.GeoJson(
    gdf,
    tooltip=folium.GeoJsonTooltip(
        fields=["id", "area_ha"],
        aliases=["Potrero", "Área (ha)"],
        localize=True
    )
).add_to(m)

# Mostrar mapa
st_folium(m, width=1200, height=600)

