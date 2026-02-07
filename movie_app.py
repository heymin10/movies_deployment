import streamlit as st
import pandas as pd
import re
import unicodedata
from google.cloud import firestore
from google.oauth2 import service_account

import json
key_dict = json.loads(st.secrets["text_key"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies-firebase")

##################################################################
################################### Definimos funciones auxiliares

#Función para leer todos los registros desde el arranque
@st.cache_data
def dataset_firestore(n_rows):
  movies_ref = list(db.collection(u'movies').stream())
  movies_dict = list(map(lambda x: x.to_dict(),movies_ref))
  return pd.DataFrame(movies_dict)

#Función para limpiar string
def clean_text(s):
  if s is None:
      return s
  # Quitar espacios al inicio/fin y normalizar espacios internos
  s = s.strip()
  s = re.sub(r"\s+", " ", s)
  # Pasar a minúsculas
  s = s.lower()
  # Quitar acentos/diacríticos
  s = unicodedata.normalize("NFKD", s)
  s = "".join(ch for ch in s if not unicodedata.combining(ch))
  return s

#Función para limpiar columna
def clean_series(col):
  return col.apply(clean_text)

#Funcion para filtrar por la columna limpia
def filtered_by_filme(df,name):
  return df[clean_series(df['name']).str.contains(clean_text(name))]

#Funcion para filtrar df
def filtered_by_director(df,name):
  return df[df['director']==name]


##################################################################
############################################## Cuerpo de streamlit

#Guardamos la base en una variable
df = dataset_firestore(10)
df_tot = df


#Creamos barra lateral de argumentos
sidebar = st.sidebar
#Checkbox para habilitar mostrar los filmes con base a sus filtros
agree = sidebar.checkbox('Mostrar todos los filmes')


#text_input para filtrar por filme
titulo_filme = sidebar.text_input('Título del filme:')
#Boton para filtrar por título de filme
btnFilterbyTitulo = sidebar.button('Buscar filmes por título')
#Filtramos por filme 
if btnFilterbyTitulo:
  df = filtered_by_filme(df,titulo_filme)


#Selectbox para seleccionar el director
selected_director = sidebar.selectbox('Seleccionar director',df['director'].unique())
#Boton para filtrar por director
btnFilterbyDirector = sidebar.button('Filtrar director')
#Filtramos por director
if btnFilterbyDirector:
  df = filtered_by_director(df,selected_director)


#Mostramos los filmes y la catidad de filmes con base a sus filtros
if agree:
  #Mostramos el total de filmes encontrados
  st.write(f'Total filmes: {len(df)}')
  #Mostramos df final
  st.dataframe(df)


#Formulario en sidebar para insetar nuevo filme
sidebar.title("Nuevo filme")
index = sidebar.text_input('Index:') 
name = sidebar.text_input('Name:')
company = sidebar.selectbox('Company:',df_tot['company'].unique())
director = sidebar.selectbox('Director:',df_tot['director'].unique())
genre = sidebar.selectbox('Genre:',df_tot['genre'].unique())
submit = sidebar.button('Crear nuevo filme')

if name and company and director and genre and submit:
  doc_ref = db.collection('movies').document(name)
  doc_ref.set({'index':index,'name':name,'company':company,'director':director,'genre':genre})
  sidebar.write('Registro insertado correctamente')
