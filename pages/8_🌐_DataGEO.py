import ast
import streamlit as st
import leafmap.foliumap as leafmap
import ee
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



@st.cache_data
def get_layers(url):
    options = leafmap.get_wms_layers(url)
    return options


def app():
    st.title("DataGEO")

    with st.expander('Descrição'):

        st.markdown(
                """
        O DataGEO é a infraestrutura de dados espaciais ambientais do Estado de São Paulo.
        O objetivo é facilitar a vida dos interessados no acesso e disponibilização das informações.
        Os dados são provenientes em sua maioria dos órgãos públicos que compõem o Sistema Ambiental Paulista. Aos dados ambientais se juntam dados cartográficos, socioeconômicos, legais e muitos outros. Tudo isso em meio digital, com navegadores da Web e sem a necessidade de cadastro.

        Referências:
        https://datageo.ambiente.sp.gov.br/ 
            """
            )
        st.image('data/logoDataGeo.png')

    row1_col1, row1_col2 = st.columns([3, 1.3])
    width = 800
    height = 600
    layers = None

    with row1_col2:

        url = "https://datageo.ambiente.sp.gov.br/geoserver/datageo/ows?SERVICE=WMS"
        empty = st.empty()

        if url:
            options = get_layers(url)

            default = None
            layers = empty.multiselect(
                "Selecione o dado", options, default=default, placeholder="Escolha uma opção"
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