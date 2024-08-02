import streamlit as st
import requests
from PIL import Image
from io import BytesIO




st.sidebar.image('data/logoder.png', width=200)


st.sidebar.title("Desenvolvido por")
st.sidebar.info(
    """
    Rafael Chasles <rafaelchasles@gmail.com> | <rgchasles@der.sp.gov.br>
    """
)




st.title('Sobre')

st.markdown("""
        
Bem-vindo ao sistema Infrasctructure Observation. 
Seu nome deriva do campo da ciência chamado
"Earth Observation" ou Observação da Terra. 
            
Apresentamos uma ferramenta que oferece uma abordagem para a análise de dados 
ambientais relacionados à infraestrutura rodoviária. Utilizamos tecnologias 
geoespaciais, incluindo sensoriamento remoto, processamento em nuvem e inteligência 
artificial para fornecer indicadores precisos e atualizados do contexto das rodovias.

Esta plataforma se destaca pela integração com o Google Earth Engine (GEE), que possui mais de 90 petabytes de 
dados de sensoriamento remoto 
permitindo análises avançadas e monitoramento em tempo quase real. Todos os dados 
utilizados provêm de fontes oficiais nacionais e internacionais, como a Agência Espacial Europeia (ESA) e a 
Administração Nacional da Aeronáutica e Espaço (NASA).
                    """)

col1, col2, col3 = st.columns(3)

with col1:

   st.image("data/GoogleEarthEngine.png", width=200)

with col2:

   st.image("data/esa1.png", width=200)

with col3:
   st.image("data/nasa.png", width=200)


st.markdown("""
            
O objetivo principal é fornecer uma ferramenta acessível e intuitiva para 
avaliar o impacto ambiental das atividades rodoviárias e seu entorno, para promover
práticas sustentáveis e resilientes. Com a plataforma, os usuários podem visualizar
e analisar dados ambientais de forma rápida e eficiente, facilitando a tomada de decisões
informadas para o desenvolvimento e gestão responsável de infraestruturas viárias.

Além dos recursos básicos de monitoramento ambiental, oferecemos uma variedade de 
ferramentas avançadas, como análise de mudança de cobertura vegetal e detecção de 
focos de incêndios florestais. Comprometemo-nos em fornecer uma solução completa para 
as necessidades de monitoramento ambiental da infraestrutura rodoviária, alinhada aos 
Objetivos de Desenvolvimento Sustentável (ODS), especialmente os relacionados às 
mudanças climáticas (ODS 13), à vida na terra (ODS 15) e infraestrutura, indústria e inovação (ODS 9).

        """)


col4, col5, col6 = st.columns(3)

with col4:

   st.image("data/ods9.jpg", width=200)

with col5:

   st.image("data/ods13.png", width=200)

with col6:
   st.image("data/ods15.png", width=200)
