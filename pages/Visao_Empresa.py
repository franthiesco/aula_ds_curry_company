#Bibliotecas necessarias
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import folium
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
from datetime import datetime


from streamlit_folium import folium_static

#from utils import clean_code - Quando se cria uma biblioteca particular de funcoes.

#Importando dados
data = pd.read_csv( 'dataset/train.csv' )
data1 = data.copy()

#Funcoes

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

def order_metric(data1):
    #Metricas dos pedidos
    cols = ['ID','Order_Date']
        
    #Selecao dos dados
    df_aux = (data1.loc[:,cols]
              .groupby('Order_Date')
              .count().
              reset_index())
        
    #Plotar os resultados
    fig = px.bar(df_aux,x='Order_Date',y='ID')
        
    return fig 

def traffic_order_share(data1):
    df_aux = (data1.loc[:,['ID','Road_traffic_density']]
              .groupby('Road_traffic_density')
              .count()
              .reset_index())
    df_aux['per_entregas'] = df_aux['ID'] / df_aux['ID'].sum()
            
    fig = px.pie(df_aux, values='per_entregas',names='Road_traffic_density')
            
    return fig


def traffic_order_city(data1):
    df_aux = (data1.loc[:,['ID','City','Road_traffic_density']]
              .groupby(['City','Road_traffic_density'])
              .count()
              .reset_index())

    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig

def order_by_week(data1):
    data1['week_of_year'] = data1['Order_Date'].dt.strftime('%U') #Filtrar datas por semana
    df_aux = (data1.loc[:,['ID','week_of_year']]
            .groupby('week_of_year')
            .count()
            .reset_index())
        
    fig = px.line(df_aux, x='week_of_year',y='ID')
            
    return fig

def order_share_by_week(data1):

    df_aux01 = (data1.loc[:,['ID','week_of_year']]
                .groupby('week_of_year')
                .count()
                .reset_index())
    df_aux02 = ((data1.loc[:,['Delivery_person_ID','week_of_year']]
                 .groupby('week_of_year')
                 .nunique()
                 .reset_index()))

    df_aux = pd.merge(df_aux01,df_aux02,how='inner',on='week_of_year')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x='week_of_year',y='order_by_deliver')

    return fig
                
def country_maps(data1):
        df_aux = (data1.loc[:, ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude'] ]
                  .groupby(['City','Road_traffic_density'])
                  .median()
                  .reset_index())
        
        map = folium.Map()
                
        for index, location_info in df_aux.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'], 
                           location_info['Delivery_location_longitude']], popup=location_info[['City','Road_traffic_density']]).add_to(map)
                
        folium_static(map, width=1024, height=600)
            
       
    

#Limpando os dados

data1 = clean_code(data1)

    #show = data1.head()

    #print(show) - TESTE SE LENDO E LIMPANDO BANCO DE DADOS
    

######## APLICANDO VISUAL E INTERACAO COM O USUARIO NO DASHBOARD #########

#Cabecalhos e visual
st.header('Marketpalce Visao Empresa')

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
        default = ['Low'])
st.sidebar.markdown("""---""")

###### APLICANDO OS FILTROS AO DASHBOARD #########

#Filtrando as datas
datas_selecionadas = data1['Order_Date'] < data_slider
data1 = data1.loc[datas_selecionadas, :]

#Filtrando as condicoes de transito
condicoes_selecionadas = data1['Road_traffic_density'].isin(traffic_options)
data1 = data1.loc[condicoes_selecionadas,:]

##### LAYOUT DO DASHBOARD #########
tab1, tab2, tab3 = st.tabs(['Visao Empresa','Visao Tatica','Visao Geografica'])

with tab1:
    with st.container():
        fig = order_metric(data1)
        st.markdown('Ordens por dia')
        st.plotly_chart(fig,use_container_width=True)
        

        
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            fig = traffic_order_share(data1)
            st.header('Traffic Order Share')
            st.plotly_chart(fig,use_container_width=True)
            
        
        with col2:
            fig = traffic_order_city(data1)
            st.header('Traffic Order City')
            st.plotly_chart(fig,use_container_width=True)
            
           

with tab2:
    with st.container():
        st.markdown('Ordens por semana')
        fig = order_by_week(data1)
        st.plotly_chart(fig, use_container_width=True)
        
        
    with st.container():
        st.markdown("#Orderns compartilhadas por semana")
        fig = order_share_by_week(data1)
        st.plotly_chart(fig,use_container_width=True)
        
        
with tab3:
    with st.container():
        st.markdown('#Country Maps')
        country_maps(data1) 
        
                
    
                
             
                
                
                
        
    
        
        
        

        
        
        
        


