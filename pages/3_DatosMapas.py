from pathlib import Path
import geopandas as gpd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
shp_path = BASE_DIR / "data" / "shp" / "pionerosPotreros.shp"

st.write("Leyendo desde:", shp_path)

gdf = gpd.read_file(shp_path)
