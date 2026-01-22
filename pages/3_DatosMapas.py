import streamlit as st
import geopandas as gpd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
shp_path = BASE_DIR / "data" / "shp" / "pionerosPotreros.shp"

gdf = gpd.read_file(shp_path)
st.map(gdp)
