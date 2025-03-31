import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import matplotlib.pyplot as plt

# def create_commune_map(coordinates_api, commune_selectionnee):
#     """Crée une carte Folium centrée sur la commune sélectionnée."""
#     if not coordinates_api or not commune_selectionnee:
#         st.warning("Données de coordonnées non disponibles.")
#         return None

#     commune_coords = coordinates_api.get(commune_selectionnee)
    
#     if not commune_coords:
#         st.warning(f"Aucune coordonnée trouvée pour {commune_selectionnee}.")
#         return None

#     commune_map = folium.Map(location=[commune_coords['lat'], commune_coords['lon']], zoom_start=10)
#     folium.Marker(
#         [commune_coords['lat'], commune_coords['lon']], 
#         popup=f"{commune_selectionnee}", 
#         tooltip="Voir la position"
#     ).add_to(commune_map)

#     return commune_map

def run_immobilier(commune_selectionnee=None, coordinates_api=None,
                   basesfiscalcommune=None, basesfiscaldepartement=None,
                   capitalimmobilier=None, capitalimmobiliercommune=None,
                   capitalimmobilierdepartement=None, isfcommunes=None,
                   terrescommunes=None):

    st.title("🏠 Capital Immobilier")

    # Vérification des DataFrames non vides
    if any(df is None for df in [basesfiscalcommune, capitalimmobilier, capitalimmobiliercommune, isfcommunes, terrescommunes]):
        st.error("❌ Erreur : certaines données ne sont pas disponibles.")
        return

    # Mapping des types d'immobilier aux DataFrames
    df_mapping = {
        "Bases fiscal commune": basesfiscalcommune,
        "Capital immobilier": capitalimmobilier,
        "ISF communes": isfcommunes,
        "Terres communes": terrescommunes,
        "Capital immobilier commune": capitalimmobiliercommune
    }
    
    # Sélection du type de capital immobilier
    type_capital_immobilier = st.sidebar.selectbox("📌 Choisissez le type d'immobilier", list(df_mapping.keys()))
    
    # Récupération du DataFrame correspondant
    df_capital_immobilier = df_mapping[type_capital_immobilier]

    if df_capital_immobilier is None or df_capital_immobilier.empty:
        st.warning(f"⚠️ Aucune donnée disponible pour {type_capital_immobilier}.")
        return

    # Sélection du département
    departements_disponibles = df_capital_immobilier['nomdep'].unique()
    departement_selectionne = st.sidebar.selectbox("📍 Sélectionnez un département", departements_disponibles)

    # Filtrer les données par département
    df_departement = df_capital_immobilier[df_capital_immobilier['nomdep'] == departement_selectionne]

    # Sélection de la commune
    communes_disponibles = df_departement['nomcommune'].unique()
    commune_selectionnee = st.sidebar.selectbox("🏘 Sélectionnez une commune", communes_disponibles)

    # Affichage des données filtrées
    st.write(f"### 📊 Données pour **{commune_selectionnee}** ({departement_selectionne})")
    
    # Sélection des colonnes à afficher
    colonnes_disponibles = df_departement.columns.tolist()
    colonnes_selectionnees = st.multiselect("📌 Sélectionnez les colonnes à afficher :", colonnes_disponibles, default=colonnes_disponibles[:5])

    if colonnes_selectionnees:
        df_filtered = df_departement[df_departement['nomcommune'] == commune_selectionnee][colonnes_selectionnees]
        st.dataframe(df_filtered)

        # Affichage des statistiques générales
        st.write("### 📈 Statistiques générales")
        st.write(df_filtered.describe())

        # Graphique en barres (Valeurs par catégorie)
        if len(colonnes_selectionnees) > 1:
            st.write("### 📊 Répartition des valeurs")
            fig = px.bar(df_filtered.melt(id_vars=['nomcommune']), x="variable", y="value", color="variable", title="Comparaison des valeurs")
            st.plotly_chart(fig)

        # Graphique circulaire (Pie Chart)
        if len(colonnes_selectionnees) > 1:
            st.write("### 🍰 Répartition des types d'immobilier")
            fig_pie = px.pie(df_filtered.melt(id_vars=['nomcommune']), names="variable", values="value", title="Proportion des valeurs")
            st.plotly_chart(fig_pie)

        # Histogramme de distribution
        st.write("### 📊 Distribution des valeurs")
        fig, ax = plt.subplots()
        df_filtered.hist(ax=ax, bins=10, grid=False)
        st.pyplot(fig)

    else:
        st.warning("⚠️ Veuillez sélectionner au moins une colonne.")

    # Affichage de la carte
    if coordinates_api:
        commune_map = create_commune_map(coordinates_api, commune_selectionnee)
        if commune_map:
            st_folium(commune_map, width=700, height=500)
    else:
        st.warning("📍 Les coordonnées de la commune ne sont pas disponibles.")
