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

# Preparing values
json_object = json.loads(json_data, strict=False)
service_account = json_object['client_email']
json_object = json.dumps(json_object)# Authorising the app
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)

st.set_page_config(layout="wide")

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

style = {

    "color": "#ff0000",
    "weight": 2,
}


trechos = 'data/trechos.geojson'

m.add_geojson(trechos, style=style, layer_name="Trechos rodoviários")

m.add_layer(buffer, name='Buffer 250m')


m.to_streamlit(height=700)