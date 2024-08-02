import streamlit as st 
import ee
import geemap.foliumap as geemap
import leafmap.foliumap as leafmap
import json
import os
import requests
from geemap import geojson_to_ee, ee_to_geojson
import datetime

st.title('Imagens de satélite')


st.sidebar.image('data/logoder.png')
st.sidebar.title("Desenvolvido por")
st.sidebar.info(
    """
    Rafael Chasles <rafaelchasles@gmail.com> | <rgchasles@der.sp.gov.br>
    """
)



with st.expander("Descrição"):
    st.write("""
             
A aplicação "Imagens de Satélite" oferece uma interface simples e intuitiva 
para explorar imagens de satélite do Sentinel-2. Com apenas alguns cliques, 
os usuários podem visualizar imagens recentes da região de seu interesse. 
Através de um seletor de datas, é possível especificar o período de tempo desejado, 
possibilitando a comparação de imagens ao longo do tempo e a análise de mudanças 
na paisagem.

Além disso, a aplicação oferece duas opções de visualização: 
"Cor Verdadeira" e "Falsa Cor". A visualização em "Cor Verdadeira" apresenta 
as imagens de forma semelhante ao que seria visto pelo olho humano, enquanto a 
visualização em "Falsa Cor" realça diferentes características da superfície terrestre, 
como vegetação saudável, água e áreas urbanas. Essas opções de visualização 
proporcionam uma compreensão mais completa da paisagem e facilitam a identificação de 
padrões e tendências ambientais.

Referências:             
https://www.esa.int/Applications/Observing_the_Earth/Copernicus/The_Sentinel_missions
             
             """)
    
    st.image('data/Sentinel2.jpeg', width=400)



json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]

# Preparing values
json_object = json.loads(json_data, strict=False)
service_account = json_object['client_email']
json_object = json.dumps(json_object)# Authorising the app
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)


col1, col2 = st.columns([7, 3])

with col1:
    today = datetime.datetime.now()
    last_year = today.year - 1
    last_year_month = today.month 
    last_year_day = today.day
    last_year_date = datetime.date(last_year, last_year_month, last_year_day)

    start = st.date_input("Data Inicial", last_year_date)
    end = st.date_input("Data Final", today)

    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

with col2:
    cloudy_pixel_percentage = st.slider("% máxima de nuvens (0 - 100%)", min_value=0, max_value=100, value=5)

buffer = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/buffer_250m")

collection = (
    ee.ImageCollection('COPERNICUS/S2_SR')
    .filterDate(start_date, end_date)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5))
)
s2 = collection.median().clip(buffer)

vis = {
    'min': 100,
    'max': 3000,
    'bands': ['B4', 'B3', 'B2'],
}

vis_false = {
    'min': 100,
    'max': 3000,
    'bands': ['B8', 'B4', 'B3'],
}

vis_false2 = {
    'min': 100,
    'max': 3000,
    'bands': ['B4', 'B8', 'B3'],
}


m = geemap.Map(center=(-22.6,-48.5), zoom=7, height=600)



style = {

    "color": "#ff0000",
    "weight": 2,
}

trechos = 'data/trechos.geojson'

m.add_geojson(trechos, style=style, layer_name="Trechos rodoviários")

m.add_layer(buffer,{}, 'Buffer 250m')

m.add_layer(s2, vis_false, 'Sentinel-2 Falsa cor vermelha', shown=False)
m.add_layer(s2, vis_false2, 'Sentinel-2 Falsa cor verde', shown=False)
m.add_layer(s2, vis, 'Sentinel-2 Cor verdadeira')

m.to_streamlit(height=700)

