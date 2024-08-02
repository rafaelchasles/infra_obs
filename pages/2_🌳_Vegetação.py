import streamlit as st
import ee
import geemap.foliumap as geemap
import json
import os
import requests
import datetime
import matplotlib.pyplot as plt

st.title('Vegetação')

st.sidebar.image('data/logoder.png')


st.sidebar.title("Desenvolvido por")
st.sidebar.info(
    """
    Rafael Chasles <rafaelchasles@gmail.com> | <rgchasles@der.sp.gov.br>
    """
)


with st.expander("Descrição"):
    st.write("""

A análise "Vegetação" oferece uma ferramenta para visualizar o Índice de Vegetação por 
Diferença Normalizada (NDVI), um indicador amplamente utilizado na avaliação da saúde 
e densidade da vegetação. O NDVI é calculado a partir das diferenças entre a refletância 
da luz vermelha e infravermelha captadas por sensores remotos. Ele varia de -1 a +1, 
onde valores mais altos indicam uma maior densidade de vegetação, enquanto valores mais 
baixos podem indicar superfícies não vegetadas, como água ou solo exposto.

Além de visualizar o NDVI no mapa, os usuários também têm a opção de exportar 
esses índices em diferentes formatos, como imagens raster ou vetoriais, para análises 
mais avançadas. Além disso, a ferramenta permite a visualização de gráficos que 
representam as variações do NDVI ao longo do tempo, possibilitando uma análise mais 
detalhada das tendências de crescimento e saúde da vegetação em uma determinada área de 
interesse. Esses recursos fornecem aos usuários insights valiosos para monitoramento 
ambiental, agricultura de precisão, estudos de mudanças climáticas e muito mais.

Referências:
https://www.sciencedirect.com/topics/earth-and-planetary-sciences/normalized-difference-vegetation-index 

""")
    


json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]


json_object = json.loads(json_data, strict=False)
json_object = json.dumps(json_object)
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

def calcula_ndvi(image):
    ndvi = image.normalizedDifference(['B8', 'B4'])
    return image.addBands(ndvi.rename('NDVI'))

m = geemap.Map(center=(-22.6,-48.5), zoom=7, height=600, data_ctrl=False, draw_ctrl=False)

collection = (
    ee.ImageCollection('COPERNICUS/S2_SR')
    .filterDate(start_date, end_date)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloudy_pixel_percentage))
    .map(calcula_ndvi)
    .select('NDVI')
)
ndvi1 = collection.median().clip(buffer)

palette_ndvi = [
    'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
    '74A901', '66A000', '529400', '3E8601', '207401', '056201',
    '004C00', '023B01', '012E01', '011D01', '011301'
]


vis_ndvi = {
    'min': 0.0,
    'max': 0.8,
    'palette': palette_ndvi
}


style = {

    "color": "#ff0000",
    "weight": 2,
}

trechos = 'data/trechos.geojson'

m.add_geojson(trechos, style=style, layer_name="Trechos rodoviários")
m.add_layer(buffer,{}, 'Buffer 250m')
m.add_layer(ndvi1, vis_ndvi, 'NDVI')

m.to_streamlit(height=700)

st.image('data/ndvi.jpeg', width=400)

import geopandas as gpd

zone_stats = ndvi1.reduceRegions(collection=buffer, reducer=ee.Reducer.median(), scale=1000, tileScale=1).getInfo()

zone_stats = gpd.GeoDataFrame.from_features(zone_stats, crs='epsg:4326')

zone_stats_sorted = zone_stats.sort_values(by='median', ascending=False).drop(columns=['geometry']).dropna()

zone_stats_filtered = zone_stats_sorted.rename(columns={'cod_rodo_1': 'Rodovias','rod_km_ini': 'Km Inicial', 'rod_km_fin': 'Km Final', 'median': 'NDVI Mediana'})

column_order = ['Rodovias', 'Km Inicial', 'Km Final', 'NDVI Mediana']

zone_stats_reordered = zone_stats_filtered[column_order]

st.dataframe(zone_stats_reordered)



import plotly.express as px

# Criar rótulos para o eixo x combinando 'cod_rod_1', 'km_ini' e 'km_fim'
x_labels = [f"{row['Rodovias']} - {row['Km Inicial']} - {row['Km Final']}" for _, row in zone_stats_reordered.iterrows()]

# Criar o gráfico de barras interativo
fig = px.bar(zone_stats_reordered, x=x_labels, y='NDVI Mediana', color='NDVI Mediana', color_continuous_scale='greens')

# Atualizar o layout do gráfico
fig.update_layout(title='Mediana de NDVI dos trechos das Rodovias Estaduais',
                  xaxis_title='Rodovia - Km Inicial - Km Final',
                  yaxis_title='NDVI Mediana')

# Exibir o gráfico no Streamlit
st.plotly_chart(fig)



#calc estatistica e exportar csv
def calcular_estatisticas_zonais(ndvi1, buffer, nome_arquivo_saida):
    out_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    path = os.path.join(out_dir, nome_arquivo_saida)

    stats = geemap.zonal_stats(
        ndvi1,
        buffer,
        path,
        stat_type='MEDIAN',
        scale=100)
    
    return path


# Definir o nome do arquivo de saída
nome_arquivo_saida = 'vegetacao_stats.csv'



def main():
    # Botão para executar a função
    if st.button("Exportar Estatísticas em .csv"):
        path = calcular_estatisticas_zonais(ndvi1, buffer, nome_arquivo_saida)
        st.success(f"Estatísticas calculadas e exportadas com sucesso! O arquivo .csv está em: {path}")

if __name__ == "__main__":
    main()
