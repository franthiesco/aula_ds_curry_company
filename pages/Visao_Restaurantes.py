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

def distance (data1, fig):
        if fig == False:
            cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']

            data1['distance'] = data1.loc[:,cols].apply(lambda x:
                                                       haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)
            media_distance = np.round(data1['distance'].mean(),2)
            
            return media_distance
        else:
            cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']

            data1['distance'] = data1.loc[:,cols].apply(lambda x:
                                                       haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)
            media_distance = data1.loc[:,['City','distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=media_distance['City'], values=media_distance['distance'], pull=[0,0.1,0])])
            
            return fig 
            
    

def media_desvio_entrega(data1, festival, funct):    
    df_aux = (data1.loc[:,['Time_taken(min)','Festival']]
              .groupby('Festival')
              .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, funct],2)
    col3.metric('Tempo Medio', df_aux)

    return df_aux

def med_des_time_graph(data1):
    df_aux = data1.loc[:,['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',x=df_aux['City'],y=df_aux['avg_time'], error_y=dict(type='data',array=df_aux['std_time'])))
    fig.update_layout(barmode='group')

    return fig

def med_des_time_traffic(data1):
    df_aux = (data1.loc[:,['City','Time_taken(min)','Road_traffic_density']]
             .groupby(['City','Road_traffic_density'])
             .agg({'Time_taken(min)':['mean','std']}))

    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City','Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig



#Limpando os dados
data1 = clean_code(data1)


#Cabecalhos e visual
st.header('Marketpalce Visao Restaurantes')

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

with tab1:
    with st.container():
        st.title("Overal Metrics")
        
        col1, col2, col3, col4, col5, col6 = st. columns(6)
        
        with col1:
            delivery_unique = len(data1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregadores',delivery_unique)
            
        with col2:
            media_distancia = distance(data1, fig=False)
            col2.metric('A distancia media em KM', media_distancia)
            
        with col3:
            df_aux = media_desvio_entrega(data1,'Yes', 'avg_time')
            col3.metric('Tempo medio em min no Festival',df_aux)
        
        with col4:
            df_aux = media_desvio_entrega(data1, 'Yes', 'std_time')
            col4.metric('Desvio tempo entrega no Festival', df_aux)
            
        with col5:
            df_aux = media_desvio_entrega(data1, 'No', 'std_time')
            col5.metric('Desvio tempo entrega', df_aux)
            
        with col6:
            df_aux = media_desvio_entrega(data1, 'No', 'avg_time')
            col6.metric('Desvio tempo entrega', df_aux)
            
    with st.container():
        st.markdown("""----""")
        
        fig = med_des_time_graph(data1)
        st.plotly_chart(fig, use_container_width=True)
            
    with st.container():
       
        df_aux = (data1.loc[:,['City','Time_taken(min)','Type_of_order']]
                  .groupby(['City','Type_of_order'])
                  .agg({'Time_taken(min)':['mean','std']}))

        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()

        st.dataframe(df_aux, use_container_width=True)
            
    with st.container():
        st.markdown("""---""")
        st.title("Distribuicao do Tempo")
        
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = distance(data1, fig=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig = med_des_time_traffic(data1)
            st.plotly_chart(fig, use_container_width=True)
            
            
    
            
            
            
                                                        
            
        
        
        
        
        
        
        
            
           
            
            
            
        
            
    
            
            
            
            
                
            

            