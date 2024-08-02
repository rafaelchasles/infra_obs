import streamlit as st 
import ee
import geemap.foliumap as geemap
import leafmap.foliumap as leafmap
import json
import os
import requests
from geemap import geojson_to_ee, ee_to_geojson
import datetime

st.title('Coberturas')



st.sidebar.image('data/logoder.png')
st.sidebar.title("Desenvolvido por")
st.sidebar.info(
    """
    Rafael Chasles <rafaelchasles@gmail.com> | <rgchasles@der.sp.gov.br>
    """
)



with st.expander("Descrição"):
    st.write("""
             
dfsdfsdfsdfsdfsdf
             
Referências:
https://sites.research.google/open-buildings/
             """)
    



json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]


json_object = json.loads(json_data, strict=False)
json_object = json.dumps(json_object)
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)



buffer = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/buffer_250m")
coberturas = ee.FeatureCollection("GOOGLE/Research/open-buildings/v3/polygons")

coberturas_clip = coberturas.filterBounds(buffer)



m = geemap.Map(center=(-22.6,-48.5), zoom=7, height=600)

m.add_basemap('HYBRID')


style = {

    "color": "#ff0000",
    "weight": 2,
}


m.add_geojson('data/trechos.geojson', style=style, layer_name="Trechos rodoviários")

m.add_layer(coberturas_clip, {}, 'Coberturas')
m.add_layer(buffer,{}, 'Buffer 250m')
m.to_streamlit(height=700)

