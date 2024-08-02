import streamlit as st
import ee
import geemap.foliumap as geemap
import json
import os
import requests
import datetime
import matplotlib.pyplot as plt

st.title('Temperatura de Superfície')

st.sidebar.image('data/logoder.png')


st.sidebar.title("Desenvolvido por")
st.sidebar.info(
    """
    Rafael Chasles <rafaelchasles@gmail.com> | <rgchasles@der.sp.gov.br>
    """
)


with st.expander("Descrição"):
    st.write("""
aosijsdjhasdlkjasdhfk

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

sp = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/sp")

buffer = ee.FeatureCollection("projects/ee-rafaelchasles-io/assets/buffer_250m")



m = geemap.Map(center=(-22.6,-48.5), zoom=7, height=600, data_ctrl=False, draw_ctrl=False)




lst = ee.ImageCollection('MODIS/061/MOD11A2').select('LST_Day_1km').filterDate(start_date, end_date)

lst_clip = lst.mean().clip(sp) 

lst_scaled = lst_clip.multiply(0.02)

lst_celsius= lst_scaled.subtract(273.15)


style = {

    "color": "#ff0000",
    "weight": 2,
}

trechos = 'data/trechos.geojson'
vis_params = {
    'min': 15,
    'max': 35,
    'palette': ['blue', 'green', 'yellow', 'red']
}
m.add_geojson(trechos, style=style, layer_name="Trechos rodoviários")

m.add_layer(lst_celsius,vis_params, 'Temperatura de Superfície')
m.add_layer(buffer,{}, 'Buffer 250m')

m.to_streamlit(height=700)



import geopandas as gpd

zone_stats = lst_celsius.reduceRegions(collection=buffer, reducer=ee.Reducer.median(), scale=1000, tileScale=1).getInfo()

zone_stats = gpd.GeoDataFrame.from_features(zone_stats, crs='epsg:4326')

zone_stats_sorted = zone_stats.sort_values(by='median', ascending=False).drop(columns=['geometry']).dropna()

zone_stats_filtered = zone_stats_sorted.rename(columns={'cod_rodo_1': 'Rodovias','rod_km_ini': 'Km Inicial', 'rod_km_fin': 'Km Final', 'median': 'LST Média'})

column_order = ['Rodovias', 'Km Inicial', 'Km Final', 'LST Média']

zone_stats_reordered = zone_stats_filtered[column_order]

st.dataframe(zone_stats_reordered)



import plotly.express as px

# Criar rótulos para o eixo x combinando 'cod_rod_1', 'km_ini' e 'km_fim'
x_labels = [f"{row['Rodovias']} - {row['Km Inicial']} - {row['Km Final']}" for _, row in zone_stats_reordered.iterrows()]

# Criar o gráfico de barras interativo
fig = px.bar(zone_stats_reordered, x=x_labels, y='LST Média', color='LST Média', color_continuous_scale='spectral_r')

# Atualizar o layout do gráfico
fig.update_layout(title='Média de Temperatura de Superfície dos trechos das Rodovias Estaduais',
                  xaxis_title='Rodovia - Km Inicial - Km Final',
                  yaxis_title='LST Média')
fig.update_yaxes(range=[17, 40])

# Exibir o gráfico no Streamlit
st.plotly_chart(fig)

