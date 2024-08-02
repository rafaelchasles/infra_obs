import streamlit as st
import datetime
import ee
import streamlit as st
import geemap.foliumap as geemap
import streamlit.components.v1 as components
import json
import geopandas as gpd

json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]


json_object = json.loads(json_data, strict=False)
json_object = json.dumps(json_object)
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)


st.sidebar.image('data/logoder.png')

st.sidebar.title("Desenvolvido por")
st.sidebar.info(
    """
    Rafael Chasles <rafaelchasles@gmail.com> | <rgchasles@der.sp.gov.br>
    """
)



st.title("Escorregamento de Terra")

with st.expander("Descrição"):
    st.write("""
             
Esta seção...aofhsodfusdfhsdçoifjasdofijasdof 
             
             """)

escorregamento = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/escorregamento")
buffer = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/buffer_250m")



m = geemap.Map(center=(-22.6,-48.5), zoom=7, height=600, data_ctrl=False, draw_ctrl=False)





style = {

    "color": "#ff0000",
    "weight": 2,
}


m.add_geojson('data/trechos.geojson', style=style, layer_name="Trechos rodoviários")

m.addLayer(escorregamento, {}, 'Escorregamento')
m.add_layer(buffer, {}, 'Buffer 250m')

m.to_streamlit(height=700)