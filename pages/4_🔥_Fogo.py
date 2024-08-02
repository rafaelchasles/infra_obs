import ast
import streamlit as st
import leafmap.foliumap as leafmap
import ee
import json



st.title('Fogo')


st.sidebar.image('data/logoder.png')


st.sidebar.title("Desenvolvido por")
st.sidebar.info(
    """
    Rafael Chasles <rafaelchasles@gmail.com> | <rgchasles@der.sp.gov.br>
    """
)



    
with st.expander("Descrição"):
    st.write("""
             
A seção "Fogo" representa uma análise que visa a identificação e visualização de 
focos de incêndio em uma determinada região. Utilizando dados de satélite do Sistema de 
Informações de Recursos de Incêndios (FIRMS), a ferramenta permite aos usuários observar 
a ocorrência de focos de incêndio em uma área específica ao longo de um período de tempo 
selecionado.
             
https://firms.modaps.eosdis.nasa.gov/ 
             
             
             """)
    st.image('data/firms.png')



json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]


json_object = json.loads(json_data, strict=False)
json_object = json.dumps(json_object)
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)



@st.cache_data
def get_layers(url):
    options = leafmap.get_wms_layers(url)
    return options


def app():

    row1_col1, row1_col2 = st.columns([3, 1.3])
    width = 800
    height = 600
    layers = None

    with row1_col2:

        url = "https://firms.modaps.eosdis.nasa.gov/mapserver/wms/fires/f3346d959193fc463554c5062862bf04/?request=getcapabilities"
        empty = st.empty() 

        if url:
            options = get_layers(url)
            layers = empty.multiselect(
                "Selecione o satélite e intervalo temporal:", options, placeholder="Escolha uma opção"
            )

        with row1_col1:
            m = leafmap.Map(center=(-22.6,-48.5), zoom=7)

            if layers is not None:
                for layer in layers:
                    m.add_wms_layer(
                        url, layers=layer, name=layer, attribution=" ", transparent=True
                    )
            
            style = {

                "color": "#ff0000",
                "weight": 2,
            }


            m.add_geojson('data/trechos.geojson', style=style, layer_name="Trechos rodoviários")
            m.to_streamlit(height=height)



 

app()

from urllib.request import urlopen 
url = "https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY=f3346d959193fc463554c5062862bf04"
  
# store the response of URL 
response = urlopen(url) 

data_json = json.loads(response.read()) 

porcentagem = data_json["current_transactions"] / 10


st.markdown("""
            O sistema da NASA FIRMS tem um limite de 1000 requisições a cada 10 minutos.
            Caso tenho consumido 100% das requisições aguarde para realizar novas consultas.
            """) 

st.metric('Você já consumiu' ,"{:.1f}%".format(porcentagem))

