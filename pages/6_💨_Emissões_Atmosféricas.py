import streamlit as st
import ee
import geemap.foliumap as geemap
import json
import os
import requests
import datetime
import matplotlib.pyplot as plt

st.title('Emissões Atmosféricas')

st.sidebar.image('data/logoder.png')


st.sidebar.title("Desenvolvido por")
st.sidebar.info(
    """
    Rafael Chasles <rafaelchasles@gmail.com> | <rgchasles@der.sp.gov.br>
    """
)


with st.expander("Descrição"):
    st.write("""
O monóxido de carbono (CO) é um importante gás traço atmosférico para entender
a química troposférica. As principais fontes de CO são a combustão de combustíveis 
fósseis, queima de biomassa e oxidação atmosférica de metano e outros hidrocarbonetos. 
Enquanto a combustão de combustíveis fósseis é a principal fonte de CO em latitudes
 médias do norte, a oxidação do isopreno e a queima de biomassa desempenham um papel 
importante nos trópicos. O TROPOMI no satélite Sentinel 5 Precursor (S5P) observa a 
abundância global de CO explorando medições de radiância da Terra em céu claro e céu 
nublado. As observações de céu claro do TROPOMI fornecem colunas totais de CO com 
sensibilidade à camada limite troposférica.
             
O metano (CH4) é, após o dióxido de carbono (CO2), o contribuinte mais importante 
para o efeito causado pelo homem. Aproximadamente três quartos das 
emissões de metano são antropogênicas e, como tal, é importante continuar o registro 
de medidas baseadas em satélites. O sensor TROPOMI, localizado no satélite Sentiel 5-P
 tem como objetivo fornecer concentrações 
de coluna de CH4 com alta sensibilidade à superfície terrestre, boa cobertura 
espaço-temporal e precisão suficiente para facilitar a modelagem inversa de fontes e 
sumidouros. O TROPOMI utiliza informações de absorção da banda de oxigênio-A (760nm) 
e da faixa espectral SWIR para monitorar as abundâncias de CH4 na atmosfera terrestre. 

Referências:
https://www.tropomi.eu/data-products/methane | 
https://www.tropomi.eu/data-products/carbon-monoxide 

""")
    st.image('data/tropomi.png', width=200,caption='Sentinel 5P')


json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]


json_object = json.loads(json_data, strict=False)
json_object = json.dumps(json_object)
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)


today = datetime.datetime.now()
last_year = today.year - 1
last_year_month = today.month 
last_year_day = today.day
last_year_date = datetime.date(last_year, last_year_month, last_year_day)
start = st.date_input("Data Inicial", last_year_date)
end = st.date_input("Data Final", today)

start_date = start.strftime("%Y-%m-%d")
end_date = end.strftime("%Y-%m-%d")

m = geemap.Map(center=(-22.6,-48.5), zoom=7, height=600, data_ctrl=False, draw_ctrl=False)

sp = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/sp")
buffer = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/buffer_250m")


co_collection = (
    ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_CO')
    .filterDate(start_date, end_date)
    .select('CO_column_number_density')
) 

ch4_collection = (
    ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_CH4')
    .filterDate(start_date, end_date)
    .select('CH4_column_volume_mixing_ratio_dry_air')
)

co = co_collection.mean().clip(sp) 
ch4 = ch4_collection.mean().clip(sp) 


band_viz_co = {
  'min': 0,
  'max': 0.05,
  'palette': ['FF0000', 'FF3333', 'FF6666', 'FF9999', 'FFCCCC']
}

band_viz_ch4 = {
    'min': 1750,
    'max': 1900,
    'palette': 'turbo'
}

m.add_basemap('HYBRID')


style = {

    "color": "#ff0000",
    "weight": 2,
}


m.add_geojson('data/trechos.geojson', style=style, layer_name="Trechos rodoviários")

m.add_layer(buffer,{}, 'Buffer 250m')
m.addLayer(co, band_viz_co, 'Monóxido de Carbono - CO', opacity=0.7)
m.addLayer(ch4, band_viz_ch4, 'Metano - CH4', opacity=0.7)

m.to_streamlit(height=700)


st.divider()
st.subheader('Metano CH4')

import geopandas as gpd

zone_stats = ch4.reduceRegions(collection=buffer, reducer=ee.Reducer.median(), scale=1000, tileScale=1).getInfo()

zone_stats = gpd.GeoDataFrame.from_features(zone_stats, crs='epsg:4326')

zone_stats_sorted = zone_stats.sort_values(by='median', ascending=False).drop(columns=['geometry']).dropna()

zone_stats_filtered = zone_stats_sorted.rename(columns={'cod_rodo_1': 'Rodovias','rod_km_ini': 'Km Inicial', 'rod_km_fin': 'Km Final', 'median': 'CH4 Mediana'})

column_order = ['Rodovias', 'Km Inicial', 'Km Final', 'CH4 Mediana']

zone_stats_reordered = zone_stats_filtered[column_order]

st.dataframe(zone_stats_reordered)



import plotly.express as px

# Criar rótulos para o eixo x combinando 'cod_rod_1', 'km_ini' e 'km_fim'
x_labels = [f"{row['Rodovias']} - {row['Km Inicial']} - {row['Km Final']}" for _, row in zone_stats_reordered.iterrows()]

# Criar o gráfico de barras interativo
fig = px.bar(zone_stats_reordered, x=x_labels, y='CH4 Mediana', color='CH4 Mediana', color_continuous_scale='turbo')

# Atualizar o layout do gráfico
fig.update_layout(title='Mediana de Metano (CH4) dos trechos das Rodovias Estaduais',
                  xaxis_title='Rodovia - Km Inicial - Km Final',
                  yaxis_title='CH4 Mediana (Mol fraction)')

fig.update_yaxes(range=[1500, max(zone_stats_reordered['CH4 Mediana'])])
# Exibir o gráfico no Streamlit
st.plotly_chart(fig)



#calc estatistica e exportar csv
def calcular_estatisticas_zonais(ch4, buffer, nome_arquivo_saida):
    out_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    path = os.path.join(out_dir, nome_arquivo_saida)

    stats = geemap.zonal_stats(
        ch4,
        buffer,
        path,
        stat_type='MEDIAN',
        scale=100)
    
    return path


# Definir o nome do arquivo de saída
nome_arquivo_saida = 'ch4_stats.csv'



def main():
    # Botão para executar a função
    if st.button("Exportar Estatísticas em .csv"):
        path = calcular_estatisticas_zonais(ch4, buffer, nome_arquivo_saida)
        st.success(f"Estatísticas calculadas e exportadas com sucesso! O arquivo .csv está em: {path}")

if __name__ == "__main__":
    main()


st.divider()
st.subheader('Monóxido de Carbono - CO')
#colocar aqui tabela, gráfico e exportação