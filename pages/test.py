import streamlit as st 
import ee
import geemap.foliumap as geemap
import leafmap.foliumap as leafmap
import json
import os
import requests
from ipyleaflet import GeoJSON
from geemap import geojson_to_ee, ee_to_geojson
import geopandas as gpd

json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]


json_object = json.loads(json_data, strict=False)
json_object = json.dumps(json_object)
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)

st.image('data/logoio.png', width=500)



st.sidebar.image('data/logoder.png')
st.sidebar.title("Desenvolvido por")
st.sidebar.info(
    """
    Rafael Chasles <rafaelchasles@gmail.com> | <rgchasles@der.sp.gov.br>
    """
)

m = geemap.Map(center=(-22.6,-48.5), zoom=7, height=600, data_ctrl=False, draw_ctrl=False)


buffer = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/buffer_250m")


ffa_db = ee.Image(ee.ImageCollection('COPERNICUS/S1_GRD') 
                       .filterBounds(buffer) 
                       .filterDate(ee.Date('2020-08-01'), ee.Date('2020-08-31')) 
                       .first() 
                       .clip(buffer))
ffa_fl = ee.Image(ee.ImageCollection('COPERNICUS/S1_GRD_FLOAT') 
                       .filterBounds(buffer) 
                       .filterDate(ee.Date('2020-08-01'), ee.Date('2020-08-31')) 
                       .first() 
                       .clip(buffer))

rgb = ee.Image.rgb(ffa_db.select('VV'),
                   ffa_db.select('VH'),
                   ffa_db.select('VV').divide(ffa_db.select('VH')))


m.add_layer(rgb, {'min': [-20, -20, 0], 'max': [0, 0, 2]}, 'FFA')




m.to_streamlit(height=700)