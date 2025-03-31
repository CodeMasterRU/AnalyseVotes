import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def run(agesexcommunes, alphabetisation, commune_selectionnee, votes_data):
    st.title("Graphique")
    st.write("Bienvenue sur la deuxième page!")

    sexe_selectionne = st.sidebar.selectbox("Sélectionnez le sexe", ["Homme", "Femme"])

    if sexe_selectionne == "Homme":
        age_columns_sexe = [col for col in agesexcommunes.columns if col.startswith('poph')]
        age_columns = [col for col in agesexcommunes.columns if col.startswith('ageh')]
    elif sexe_selectionne == "Femme":
        age_columns_sexe = [col for col in agesexcommunes.columns if col.startswith('popf')]
        age_columns = [col for col in agesexcommunes.columns if col.startswith('agef')]

    st.sidebar.subheader(f"Choisissez un groupe d'âge pour {sexe_selectionne}")
    age_label = st.sidebar.selectbox("Groupe d'âge", age_columns_sexe)

    age_data_filtered = agesexcommunes[agesexcommunes['nomcommune'] == commune_selectionnee]

    max_age_groups = 10
    age_columns_sexe_limited = age_columns_sexe[:max_age_groups]

    st.sidebar.subheader("Sélectionnez une année d'alphabétisation")
    annee_alphabetisation = st.sidebar.selectbox("Année", [1866, 1871, 1876, 1882, 1887, 1890, 1895, 1900, 1905, 1910, 1915, 1920, 1925, 1930, 1935, 1940, 1945, 1946])

    alpha_column = f'alpha{annee_alphabetisation}'
    alpha_data_filtered = alphabetisation[alphabetisation['nomcommune'] == commune_selectionnee]

    if not age_data_filtered.empty:
        population_age = age_data_filtered[age_label].values[0]
        st.success(f"Population {sexe_selectionne} dans le groupe d'âge {age_label} à {commune_selectionnee}: {population_age}")

        st.subheader(f"Répartition de la population {sexe_selectionne} par groupe d'âge à {commune_selectionnee}")
        population_values = age_data_filtered[age_columns_sexe_limited].values.flatten()

        plt.figure(figsize=(10, 6))
        sns.barplot(x=age_columns_sexe_limited, y=population_values, palette='viridis')
        plt.xticks(rotation=45)
        plt.xlabel("Groupe d'âge")
        plt.ylabel("Population")
        st.pyplot(plt)

    if not alpha_data_filtered.empty:
        st.subheader("Évolution de l'alphabétisation au fil des années")
        years = ['1866', '1871', '1876', '1882', '1887', '1890', '1895', '1900', '1905', '1910', '1915',
                '1920', '1925', '1930', '1935', '1940', '1945', '1946']
        alpha_values = alpha_data_filtered[[f'alpha{year}' for year in years]].values.flatten()
        plt.figure(figsize=(12, 6))
        plt.plot(years, alpha_values, marker='o', color='teal')
        plt.title(f"Évolution de l'alphabétisation à {commune_selectionnee}")
        plt.xlabel("Année")
        plt.ylabel("Alphabétisation")
        st.pyplot(plt)
    else:
        st.warning("Aucune donnée d'alphabétisation disponible pour cette commune.")

    if not votes_data.empty:
        st.subheader("Répartition des voix par candidat")
        voix_columns = [col for col in votes_data.columns if col.startswith('voix')]
        voix_data = votes_data[voix_columns].sum()
        plt.figure(figsize=(12, 6))
        sns.barplot(x=voix_data.index, y=voix_data.values, palette='magma')
        plt.xticks(rotation=45)
        plt.xlabel("Candidat")
        plt.ylabel("Nombre de voix")
        plt.title(f"Répartition des voix par candidat à {commune_selectionnee}")
        st.pyplot(plt)
    else:
        st.warning("Aucune donnée de voix disponible pour cette commune.")
