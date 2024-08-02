import datetime
import ee
import streamlit as st
import geemap.foliumap as geemap
import streamlit.components.v1 as components
import json

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


st.title("Uso e Ocupação da Terra")


with st.expander("Descrição"):
    st.write("""
             
"Uso e Ocupação da Terra" representa uma análise que permite aos usuários visualizar e 
analisar padrões de uso da terra em uma determinada região ao longo do tempo. Utilizando 
dados do Dynamic World, a ferramenta exibe informações sobre a cobertura e uso da terra,
mostrando as mudanças ocorridas em diferentes períodos de tempo. O mapa resultante mostra 
a classificação da cobertura da terra em diferentes categorias, como florestas, agricultura,
áreas urbanas, entre outras, permitindo uma compreensão detalhada dos padrões de uso da 
terra na região em questão.

Além da visualização dos padrões de uso da terra, a ferramenta oferece recursos adicionais 
de análise, incluindo a possibilidade de extrair estatísticas das porcentagens das classes 
de uso e ocupação do solo. Os usuários podem também visualizar gráficos de Sankey, que 
mostram as mudanças na distribuição das classes de uso da terra de um período para outro, 
fornecendo insights valiosos sobre as tendências e padrões de mudança na paisagem ao longo 
do tempo. Esses recursos adicionais permitem uma análise mais detalhada e uma compreensão 
mais completa dos processos de uso da terra na região.   

Referências:
https://dynamicworld.app/    
             """)
    st.image('data/dynamicworld.png')


col1, col2 = st.columns([4, 1])

m = geemap.Map()
m.add_basemap("HYBRID")


with col2:

    m.setCenter(-48.5,-22.6, 7)

    today = datetime.datetime.now()
    last_year = today.year - 1
    last_year_month = today.month 
    last_year_day = today.day
    last_year_date = datetime.date(last_year, last_year_month, last_year_day)

    start = st.date_input("Data inicial", last_year_date)
    end = st.date_input("Data final", today)

    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

    buffer = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/buffer_250m")

    dw = geemap.dynamic_world(buffer, start_date, end_date, return_type="hillshade")
    esa_lulc = ee.ImageCollection('ESA/WorldCover/v200').first()

    dw_clip = dw.clip(buffer)
    esa_lulc_clip = esa_lulc.clip(buffer)

    st.image('data/dw.jpeg',width=200)
    st.image('data/mapbiomas.jpeg',width=200)
    st.image('data/esa_2020.jpeg',width=200)



    style = {

        "color": "#ff0000",
        "weight": 2,
    }


    m.add_geojson('data/trechos.geojson', style=style, layer_name="Trechos rodoviários")


    m.add_layer(buffer,{}, 'Buffer 250m')

    m.add_layer(dw_clip, {}, 'Dynamic Word - Uso e Cobertura da Terra')


    m.add_layer(esa_lulc_clip, {}, 'ESA - Uso e Cobertura da Terra 2021', shown=False)
    

with col1:
    m.to_streamlit(height=750)