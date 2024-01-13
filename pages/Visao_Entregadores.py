#Bibliotecas necessarias
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import folium
import pandas as pd
import streamlit as st
from PIL import Image
from datetime import datetime
import numpy as np


from streamlit_folium import folium_static

#from utils import clean_code - Quando se cria uma biblioteca particular de funcoes.

#Importando dados
data = pd.read_csv( 'dataset/train.csv' )
data1 = data.copy()


# ---------------------------
# FUNCOES
# ---------------------------

def clean_code(data1):
    '''Funcao tem a responsabilidade de limpar o dataframe
    
         - Remocao dos Nan
         - Mudana tipo de dados das colunas necessarias
         - Remocao dos espacos
         - Formatacao das colunas datas
         - Limpeza coluna tempo, remocao (min)'''
    
    #Removendo NaN
    selecao = (data1['Delivery_person_Age'] != 'NaN ')
    #data1 = data1.loc[selecao, :].copy()
    
    selecao = (data1['Weatherconditions'] != 'conditions NaN')
    #data1 = data1.loc[selecao,:].copy()
    
    selecao = (data1['Road_traffic_density'] != 'NaN ')
    #data1 = data1.loc[selecao, :].copy()

    selecao = (data1['City'] != 'NaN ')
    #data1 = data1.loc[selecao, :].copy()

    selecao = (data1['Festival'] != 'NaN ')
    #data1 = data1.loc[selecao, :].copy()

    #Converter object para int coluna Age
    data1['Delivery_person_Age'] = data1['Delivery_person_Age'].astype( float )

    #Converter object para float coluna Ratings
    data1['Delivery_person_Ratings'] = data1['Delivery_person_Ratings'].astype(float)

    #Definir data como data
    data1['Order_Date'] = pd.to_datetime(data1['Order_Date'], format='%d-%m-%Y')

    #Converter mupltiple delivery para int
    data1['multiple_deliveries'] = data1['multiple_deliveries'].astype(float)

    #Removendo especos
    data1.loc[:,'ID'] = data1.loc[:,'ID'].str.strip()
    data1.loc[:,'Weatherconditions'] = data1.loc[:,'Weatherconditions'].str.strip()
    data1.loc[:,'Road_traffic_density'] = data1.loc[:,'Road_traffic_density'].str.strip()
    data1.loc[:,'Type_of_order'] = data1.loc[:,'Type_of_order'].str.strip()
    data1.loc[:,'Type_of_vehicle'] = data1.loc[:,'Type_of_vehicle'].str.strip()
    data1.loc[:,'City'] = data1.loc[:,'City'].str.strip()
    data1.loc[:,'Festival'] = data1.loc[:,'Festival'].str.strip()

    #Limpando coluna time taken
    data1['Time_taken(min)'] = data1['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1])
    data1['Time_taken(min)'] = data1['Time_taken(min)'].astype(int)
    
    return data1

def top_delivers(data2, top_asc):
    data2 = (data1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
            .groupby(['City','Delivery_person_ID'])
            .mean()
            .sort_values(['City','Time_taken(min)'], ascending=top_asc)
            .round(2)
            .reset_index())
    df_aux01 = data2.loc[data2['City'] == 'Metropolitian',:].head(10)
    df_aux02 = data2.loc[data2['City'] == 'Urban',:].head(10)
    df_aux03 = data2.loc[data2['City'] == 'Semi-Urban',:].head(10)
    data3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    
    return data3 


#Limpando os dados
data1 = clean_code(data1)


#Cabecalhos e visual
st.header('Marketpalce Visao Entregadores')

st.sidebar.markdown('# Cury Company')

#Opcoes para o usuario
data_slider = st.sidebar.slider(
        'Periodo desejado?',
        value = datetime(2022,4,13),
        min_value = datetime(2022,2,11),
        max_value = datetime(2022,4,13),
        format='DD-MM-YYYY')
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
        'Quais as condicoes de transito desejado?',
        ['Low','Medium','High','Jam'],
        default = ['Low','Medium','High','Jam'])
st.sidebar.markdown("""---""")

###### APLICANDO OS FILTROS LATERAL AO DASHBOARD #########

#Filtrando as datas
datas_selecionadas = data1['Order_Date'] < data_slider
data1 = data1.loc[datas_selecionadas, :]

#Filtrando as condicoes de transito
condicoes_selecionadas = data1['Road_traffic_density'].isin(traffic_options)
data1 = data1.loc[condicoes_selecionadas,:]



##### LAYOUT DO DASHBOARD #########
tab1, tab2, tab3 = st.tabs(['Visao Gerencial','-','-'])

with tab1: #
    with st.container():
        st.title('Informacoes gerais')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        ### Maneira de modular as 4 colunas abaixo
        #def calculate_big_numbers (col, operation):
            #if operation == 'max'
                #resultado = data1.loc[:,col].max()
            
            #elif operation == 'min'
                #resultado = data1.loc[:,col].min()
                
            #return resultado
        
        #with col1:
            #maior_idade = calculate_big_numbers('Delivery_person_Age', operation='max')
            #col1.metric('Maior Idade',maior_idade)
            
        with col1:
            #Maior idade dos entregadores
            maior_idade = data1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior Idade',maior_idade)
            
        with col2:
            #Menor idade dos entregadores
            menor_idade = data1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor Idade',menor_idade)
            
        with col3:
            #Melhor condicao entregadores
            melhor_condicao = data1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condicao',melhor_condicao)
        with col4:
            #Pior condicao entregadores
            pior_condicao = data1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condicao',pior_condicao)
            

    with st.container():
        st.markdown( """---""")
        st.title('Avaliacoes')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('Avaliacao media por entregador')
            media_entregador = (data1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
                               .groupby('Delivery_person_ID')
                               .mean()
                               .reset_index()
                               .round(2))
            st.dataframe(media_entregador)
            
        with col2:
            st.markdown('Avaliacao media por transito')
            media_transito = (data1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                             .groupby('Road_traffic_density')
                             .agg({'Delivery_person_Ratings':['mean','std']})
                             .round(2))
            
            #mudanca nome das colunas
            media_transito.columns = ['delivery_mean','delivery_std']
            
            #reset do index
            media_transito = media_transito.reset_index()
            st.dataframe(media_transito)
            
            
            st.markdown('Avaliacao media por clima')
            media_clima = (data1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                          .groupby('Weatherconditions')
                          .agg({'Delivery_person_Ratings':['mean','std']})
                          .round(2))
            #mudanca nome das colunas
            media_clima.columns = ['delivery_mean','delivery_std']
            
            #reset do index
            media_clima = media_clima.reset_index()
            st.dataframe(media_clima)
            
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('Top entregadores mais rapidos')
            data3 = top_delivers(data1, top_asc=True)            
            st.dataframe(data3)

            
        with col2:
            st.markdown('Entregadores mais lentos')
            data3 = top_delivers(data1, top_asc=False)
            st.dataframe(data3)
            
            
            
            
            
            
            
        
            
        


