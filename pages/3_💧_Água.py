import streamlit as st 
import ee
import geemap.foliumap as geemap
import leafmap.foliumap as leafmap
import json
import os
import requests
from geemap import geojson_to_ee, ee_to_geojson
import datetime
import geemap.colormaps as cm



st.title('Água')


st.sidebar.image('data/logoder.png')
st.sidebar.title("Desenvolvido por")
st.sidebar.info(
    """
    Rafael Chasles <rafaelchasles@gmail.com> | <rgchasles@der.sp.gov.br>
    """
)



    
with st.expander("Descrição"):
    st.write("""
             
             
A análise "Água" oferece uma ferramenta para visualizar a presença de água em uma 
determinada região, utilizando os índices de NDWI (Índice de Água Normalizado) e 
NDMI (Índice de Umidade do Solo Normalizado). Esses índices são calculados a partir 
das imagens de satélite do Sentinel-2, permitindo a detecção de corpos d'água e umidade 
do solo.

Além de visualizar a presença de água, os usuários também podem utilizar essa ferramenta 
para identificar áreas que possam ter passado por inundações, pois o NDWI e o NDMI são 
sensíveis à presença de água em diferentes formas, como rios, lagos e solo úmido. 
Com um seletor de datas, os usuários podem especificar o período de tempo desejado para 
análise, possibilitando a observação de mudanças na distribuição da água ao longo do tempo.

Além disso, a ferramenta oferece a opção de exportar esses índices em diferentes formatos, 
como tabelas ou em formato vetoriais, e também permite visualizar gráficos que representam
as variações do NDWI e NDMI ao longo do tempo, fornecendo insights valiosos para
monitoramento ambiental, gestão de recursos hídricos e estudos de mudanças climáticas.

Referências:
https://www.sciencedirect.com/science/article/abs/pii/S0034425796000673      
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

inundacao = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/inundacao")

def calcula_ndwi(image):
    ndwi = image.normalizedDifference(['B3', 'B8'])
    return image.addBands(ndwi.rename('NDWI')).select('NDWI')

def calcula_ndmi(image):
    ndmi = image.normalizedDifference(['B8', 'B11'])
    return image.addBands(ndmi.rename('NDMI')).select('NDMI')

m = geemap.Map(center=(-22.6,-48.5), zoom=7, height=600, data_ctrl=False, draw_ctrl=False)
m.add_basemap('HYBRID')

collection = (
    ee.ImageCollection('COPERNICUS/S2_SR')
    .filterDate(start_date, end_date)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5)).map(calcula_ndwi)
)
ndwi1 = collection.median().clip(buffer).select('NDWI')

collection2 = (
    ee.ImageCollection('COPERNICUS/S2_SR')
    .filterDate(start_date, end_date)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5)).map(calcula_ndmi)
)
ndmi1 = collection2.median().clip(buffer).select('NDMI')


palette_ndwi = [
    'FFFFFF00', 'C2D9FF', 'A4CAE9', '88B1D9', '6D98C6', '547FAE',
    '3C6697', '235485', '113374', '002961', '00144E'
]


vis_ndwi = {
    'min': 0.0,
    'max': 0.1,
    'opacity':0.6,
    'palette': palette_ndwi
}

palette_ndmi = cm.palettes.ndwi

vis_ndmi = {
    'min': 0.0,
    'max': 0.1,
    'opacity':0.6,
    'palette': palette_ndmi
}


style = {

    "color": "#ff0000",
    "weight": 2,
}


m.add_geojson('data/trechos.geojson', style=style, layer_name="Trechos rodoviários")
m.add_layer(buffer,{}, 'Buffer 250m')
m.add_layer(ndwi1.select('NDWI'), vis_ndwi, 'NDWI')
m.add_layer(ndmi1.select('NDMI'), vis_ndmi, 'NDMI', shown=False)
m.add_layer(inundacao, {}, "Áreas sucetíveis a Alagamento", shown=False)


m.to_streamlit(height=700)

st.image('data/ndwi.jpeg', width=400)


import geopandas as gpd

#NDWI
zone_stats = ndwi1.reduceRegions(collection=buffer, reducer=ee.Reducer.median(), scale=1000, tileScale=1).getInfo()

zone_stats = gpd.GeoDataFrame.from_features(zone_stats, crs='epsg:4326')

zone_stats_sorted = zone_stats.sort_values(by='median', ascending=False).drop(columns=['geometry']).dropna()

zone_stats_filtered = zone_stats_sorted.rename(columns={'cod_rodo_1': 'Rodovias','rod_km_ini': 'Km Inicial', 'rod_km_fin': 'Km Final', 'median': 'MEDIAN NDWI'})

column_order = ['Rodovias', 'Km Inicial', 'Km Final', 'MEDIAN NDWI']

zone_stats_reordered = zone_stats_filtered[column_order]

st.dataframe(zone_stats_reordered)



import plotly.express as px

# Criar rótulos para o eixo x combinando 'cod_rod_1', 'km_ini' e 'km_fim'
x_labels = [f"{row['Rodovias']} - {row['Km Inicial']} - {row['Km Final']}" for _, row in zone_stats_reordered.iterrows()]

# Criar o gráfico de barras interativo
fig = px.bar(zone_stats_reordered, x=x_labels, y='MEDIAN NDWI', color='MEDIAN NDWI', color_continuous_scale='blues')

# Atualizar o layout do gráfico
fig.update_layout(title='Mediana de NDWI dos trechos das Rodovias Estaduais',
                  xaxis_title='Rodovia - Km Inicial - Km Final',
                  yaxis_title='NDWI Mediana')

# Exibir o gráfico no Streamlit
st.plotly_chart(fig)


#calc estatistica e exportar csv
def calcular_estatisticas_zonais(nwdi1, buffer, nome_arquivo_saida):
    out_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    path = os.path.join(out_dir, nome_arquivo_saida)

    stats = geemap.zonal_stats(
        ndwi1,
        buffer,
        path,
        stat_type='MEDIAN',
        scale=1000)
    
    return path


# Definir o nome do arquivo de saída
nome_arquivo_saida = 'agua_stats.csv'



def main():
    # Botão para executar a função
    if st.button("Exportar Estatísticas em .csv"):
        path = calcular_estatisticas_zonais(ndwi1, buffer, nome_arquivo_saida)
        st.success(f"Estatísticas calculadas e exportadas com sucesso! O arquivo .csv está em: {path}")

if __name__ == "__main__":
    main()
