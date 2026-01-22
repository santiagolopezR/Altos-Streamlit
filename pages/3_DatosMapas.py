import streamlit as st
import geopandas as gpd
from pathlib import Path
import folium
from streamlit_folium import st_folium

import geopandas as gpd

gdf = gpd.read_file("pionerosPotreros.shp")
gdf.to_file("pionerosPotreros.geojson", driver="GeoJSON")

