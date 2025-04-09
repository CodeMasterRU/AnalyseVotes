import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import logging
import requests
import json
import plotly.graph_objects as go
import numpy as np

def get_coordinates(city_name):
    url = f"https://nominatim.openstreetmap.org/search?q={city_name},+France&format=json"
    headers = {'User-Agent': 'MonApplication/1.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data:
            lat, lon = float(data[0]['lat']), float(data[0]['lon'])
            logging.info(f"Coordonnées trouvées pour {city_name}: Latitude {lat}, Longitude {lon}")
            return lat, lon
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur de requête pour {city_name}: {e}")
    return None

def create_commune_map(commune_coordinates=None):
    m = folium.Map(location=[46.6034, 1.8883], zoom_start=5)
    try:
        with open('./Data/GeoJson/departements_uppercase_fixed.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        folium.GeoJson(geojson_data, name='geojson').add_to(m)
    except FileNotFoundError:
        logging.error("Fichier departements.geojson non trouvé.")

    if commune_coordinates:
        folium.Marker(
            location=commune_coordinates,
            popup=f"Commune sélectionnée",
            icon=folium.Icon(color='blue')
        ).add_to(m)
    
    folium.LayerControl().add_to(m)
    return m

def run_elections(pres_df, leg_df, diplomes_communes, diplomes_departements):
    st.title("Analyse des élections et de l'éducation en France")
    
    # Существующий код для карты
    type_election = st.sidebar.selectbox("Choisissez le type d'élection", ["Présidentielle", "Législative"])
    df_election = pres_df if type_election == "Présidentielle" else leg_df

    departement_selectionne = st.sidebar.selectbox("Sélectionnez un département", df_election['nomdep'].unique())
    df_departement = df_election[df_election['nomdep'] == departement_selectionne]

    commune_selectionnee = st.sidebar.selectbox("Sélectionnez une commune", df_departement['nomcommune'].unique())
    coordinates_api = get_coordinates(commune_selectionnee)

    if coordinates_api:
        departement_map = create_commune_map(coordinates_api)
        st_folium(departement_map, width=700, height=500)
    else:
        st.warning(f"Impossible de récupérer les coordonnées pour {commune_selectionnee}.")

    # Добавляем анализ образования
    st.header("Analyse du niveau d'éducation")

    # График тенденций образования по департаментам
    st.subheader("Tendances de l'éducation par département")
    
    selected_year = st.selectbox("Sélectionnez l'année", range(2010, 2023))
    
    # График 1: Тенденции образования по департаментам
    fig1 = go.Figure()
    top_deps = diplomes_departements.nlargest(5, f'sup{selected_year}')
    fig1.add_trace(go.Bar(
        x=top_deps['nomdep'],
        y=top_deps[f'sup{selected_year}'],
        name='Niveau supérieur'
    ))
    fig1.update_layout(
        title=f'Top-5 départements par niveau d\'éducation ({selected_year})',
        xaxis_title='Département',
        yaxis_title='Nombre de diplômés'
    )
    st.plotly_chart(fig1)

    # График 2: Анализ по полу
    st.subheader("Tendances de l'éducation par sexe")
    selected_dept = st.selectbox("Sélectionnez un département pour l'analyse par sexe", 
                               diplomes_departements['nomdep'].unique())
    
    dept_data = diplomes_communes[diplomes_communes['nomdep'] == selected_dept]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name='Hommes',
        x=['Supérieur', 'Bac', 'Sans diplôme'],
        y=[
            dept_data[f'suph{selected_year}'].sum(),
            dept_data[f'bach{selected_year}'].sum(),
            dept_data[f'nodiph{selected_year}'].sum()
        ]
    ))
    fig2.add_trace(go.Bar(
        name='Femmes',
        x=['Supérieur', 'Bac', 'Sans diplôme'],
        y=[
            dept_data[f'supf{selected_year}'].sum(),
            dept_data[f'bacf{selected_year}'].sum(),
            dept_data[f'nodipf{selected_year}'].sum()
        ]
    ))
    fig2.update_layout(
        barmode='group',
        title=f'Répartition par sexe et niveau d\'éducation - {selected_dept} ({selected_year})'
    )
    st.plotly_chart(fig2)