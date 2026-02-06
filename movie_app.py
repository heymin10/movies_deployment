import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account

import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies")

def dataset_firestore():
  movies_ref = list(db.collection(u'movies').stream())
  movies_dict = list(map(lambda x: x.to_dict(),movies_ref))
  return pd.DataFrame(movies_dict)

sidebar = st.sidebar
agree = sidebar.checkbox('Mostrar todos los filmes')
sidebar.write('Título del filme:')
titulo_filme = sidebar.text_input()

df_final = dataset_firestore()

if agree:
  st.dataframe(df_final)
