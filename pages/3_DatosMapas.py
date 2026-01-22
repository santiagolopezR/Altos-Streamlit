import pandas as pd
import geopandas as gpd
gdf = gpd.read_file("data/shp/pionerosPotreros.shp")

st.write(gdf.head())
