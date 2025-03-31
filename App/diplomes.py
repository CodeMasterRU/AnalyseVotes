import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def run1(diplomes_communes, diplomes_departements, pres_df, legis_df=None):
    st.title("Analyse du niveau d'éducation en France")
    
    # Выводим названия колонок для отладки
    st.write("Disponibilités de colonnes dans les données des élections:")
    st.write(pres_df.columns.tolist())
    
    # Добавляем выбор типа выборов
    election_type = st.sidebar.radio(
        "Sélectionnez le type d'élection",
        ('Présidentielle', 'Législative')
    )
    
    # Подготавливаем данные в зависимости от выбора
    if election_type == 'Présidentielle':
        election_df = pres_df
        # Получаем список колонок, начинающихся с 'voix'
        vote_columns = [col for col in pres_df.columns if col.startswith('voix')]
        # Создаем список имен кандидатов, убирая префикс 'voix'
        candidates = [col[4:] for col in vote_columns]
    else:  # Législative
        if legis_df is not None:
            election_df = legis_df
            vote_columns = [col for col in legis_df.columns if col.startswith('voix')]
            candidates = [col[4:] for col in vote_columns]
        else:
            st.error("Les données des élections législatives ne sont pas disponibles")
            return
    
    # 1. Объединение данных о дипломах и выборах
    merged_df = pd.merge(election_df, diplomes_communes, on='codecommune', how='inner')
    
    # Добавление переменной процента людей с высшим образованием
    merged_df['percent_high_edu'] = (merged_df['suph1962'] + merged_df['supf1962']) / (merged_df['nodiph1962'] + merged_df['nodipf1962']) * 100
    
    # Создаем корреляционный анализ для всех кандидатов/партий
    st.subheader(f"Correlation entre le niveau d'éducation et les votes ({election_type})")
    
    if len(vote_columns) > 0:
        # Создаем вкладки для разных визуализаций
        tab1, tab2, tab3 = st.tabs(["Graphique de dispersion", "Matrice de correlation", "Graphique suplementaire"])
        
        with tab1:
            # Pозволяем пользователю выбрать кандидата/партию для анализа
            selected_candidate = st.selectbox(
                "Choisissez un candidat/parti pour analyser",
                range(len(candidates)),
                format_func=lambda x: candidates[x]
            )
            
            # Graphique de dispersion pour выбранного кандидата/партии
            fig1 = px.scatter(merged_df, 
                             x='percent_high_edu', 
                             y=vote_columns[selected_candidate],
                             title=f'Correlation entre le niveau d\'education et les votes pour {candidates[selected_candidate]} ({election_type})',
                             labels={'percent_high_edu': 'Pourcentage de personnes avec un niveau d\'education supérieur (%)',
                                    vote_columns[selected_candidate]: f'Nombre de votes pour {candidates[selected_candidate]}'})
            
            # Ajout de la ligne de tendance
            fig1.add_traces(
                px.scatter(merged_df, 
                          x='percent_high_edu', 
                          y=vote_columns[selected_candidate],
                          trendline="ols").data[1]
            )
            st.plotly_chart(fig1)
            
            # Calcul et affichage du coefficient de correlation
            correlation = merged_df['percent_high_edu'].corr(merged_df[vote_columns[selected_candidate]])
            st.write(f"Coef de correlation: {correlation:.3f}")
            
        with tab2:
            # Création de la matrice de correlation
            corr_data = merged_df[['percent_high_edu'] + vote_columns].corr()
            
            # Création d'une carte de chaleur pour la matrice de correlation
            fig2 = go.Figure(data=go.Heatmap(
                z=corr_data.values,
                x=['Niveau d\'education'] + candidates,
                y=['Niveau d\'education'] + candidates,
                colorscale='RdBu',
                zmin=-1,
                zmax=1
            ))
            
            fig2.update_layout(
                title='Correlation entre le niveau d\'education et les votes pour chaque candidat',
                width=700,
                height=700
            )
            st.plotly_chart(fig2)
        
        with tab3:
            # Graphiques supplémentaires depuis diplomes_pres.ipynb
            st.subheader("Graphiques supplémentaires")
            # Préparation des données
            fig3 = plt.figure(figsize=(10, 6))
            plt.plot(merged_df['codecommune'], merged_df['percent_high_edu'], label='Niveau d\'education')
            plt.xlabel('Code de la commune')
            plt.ylabel('Pourcentage de personnes avec un niveau d\'education supérieur (%)')
            plt.title("Pourcentage de l'enseignement supérieur par commune")
            plt.legend()
            st.pyplot(fig3)
    
    else:
        st.error("Il n'y a aucune donnée de vote dans l'ensemble de données sélectionné.")
    
    # Ajout du texte d'exploration des données
    st.markdown("""
    ### Interprétation des résultats:
    
    - Correlation positive (proche de 1) indique une relation positive entre le niveau d'education et les votes
    - Correlation negative (proche de -1) indique une relation negative entre le niveau d'education et les votes
    - Correlation proche de 0 indique une absence de relation claire entre le niveau d'education et les votes
    
    Observez que la correlation ne signifie pas une cause-effet.
    """)
    
    # 2. Tendances de l'éducation par département
    st.subheader("Tendances de l'education par département")
    
    # Choisissez un top-5 des départements avec le plus de personnes avec un niveau d'education supérieur
    top_deps = diplomes_departements.nlargest(5, 'psup2022')[['nomdep', 'psup2022']]
    
    # Créer un graphique des tendances
    fig2 = go.Figure()
    
    years = range(2010, 2023)
    for dep in top_deps['nomdep']:
        values = [diplomes_departements[diplomes_departements['nomdep'] == dep][f'psup{year}'].iloc[0] for year in years]
        fig2.add_trace(go.Scatter(x=list(years), y=values, name=dep, mode='lines+markers'))
    
    fig2.update_layout(
        title='Tendances de l\'education dans les top-5 departements (2010-2022)',
        xaxis_title='Année',
        yaxis_title='Pourcentage de personnes avec un niveau d\'education supérieur (%)',
        hovermode='x unified'
    )
    st.plotly_chart(fig2)
    
    # 3. Génère un graphique des tendances de l'education par sexe
    st.subheader("Génère un graphique des tendances de l'education par sexe")
    
    # Calcul des moyennes par sexe
    years_gender = range(1945, 1963)
    gender_gap_data = {
        'Année': [],
        'Hommes': [],
        'Femmes': []
    }
    
    for year in years_gender:
        if f'suph{year}' in diplomes_communes.columns and f'supf{year}' in diplomes_communes.columns:
            gender_gap_data['Année'].append(year)
            gender_gap_data['Hommes'].append(diplomes_communes[f'suph{year}'].mean())
            gender_gap_data['Femmes'].append(diplomes_communes[f'supf{year}'].mean())
    
    gender_df = pd.DataFrame(gender_gap_data)
    
    fig3 = px.line(gender_df, 
                   x='Année', 
                   y=['Hommes', 'Femmes'],
                   title="Inégalités entre les sexes dans l'enseignement supérieur (1945-1962)",
                   labels={'value': 'Moyenne des personnes avec un niveau d\'education supérieur (%)',
                          'variable': 'Sexe'})
    st.plotly_chart(fig3)
    
    # 4.Répartition des niveaux d'éducation par commune (par année)
    st.subheader("Répartition du niveau d'éducation par communes selon les années")
    
    # Créer un DataFrame avec les pourcentages de l'enseignement supérieur par année
    edu_by_year = pd.DataFrame()
    
    # Nous sélectionnons des années avec un intervalle de 10 ans pour plus de clarté
    selected_years = [1945, 1955, 1965, 1975, 1985, 1995, 2005, 2015, 2022]
    
    for year in selected_years:
        if f'suph{year}' in diplomes_communes.columns and f'supf{year}' in diplomes_communes.columns and \
           f'nodiph{year}' in diplomes_communes.columns and f'nodipf{year}' in diplomes_communes.columns:
            
            total_edu = diplomes_communes[f'suph{year}'] + diplomes_communes[f'supf{year}']
            total_pop = diplomes_communes[f'nodiph{year}'] + diplomes_communes[f'nodipf{year}']
            edu_by_year[str(year)] = (total_edu / total_pop * 100).clip(0, 100)  # Limit values between 0 and 100%
    
    # Créer un graphique
    fig4 = go.Figure()
    
    # Ajouter des histogrammes pour chaque année
    colors = px.colors.qualitative.Set3
    for i, year in enumerate(edu_by_year.columns):
        fig4.add_trace(go.Histogram(
            x=edu_by_year[year].dropna(),
            name=f'{year} год',
            nbinsx=50,
            opacity=0.7,
            marker_color=colors[i % len(colors)]
        ))
    
    # Настраиваем внешний вид
    fig4.update_layout(
        title={
            'text': 'Répartition du pourcentage de personnes ayant fait des études supérieures par commune (dynamique par année)',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Pourcentage de personnes avec un niveau d\'education supérieur (%)',
        yaxis_title='Nombre de communes',
        barmode='overlay',
        bargap=0.1,
        showlegend=True,
        legend_title='Année',
        plot_bgcolor='white',
        xaxis=dict(
            gridcolor='lightgray',
            zerolinecolor='gray',
            range=[0, edu_by_year.quantile(0.99).max()]  # Limitez la portée pour une meilleure visualisation
        ),
        yaxis=dict(
            gridcolor='lightgray',
            zerolinecolor='gray'
        )
    )
    
    # Ajoutez des statistiques de base
    stats_text = "Statistiques de la distribution par année:\n"
    for year in edu_by_year.columns:
        stats = edu_by_year[year].describe()
        stats_text += f"\n{year} год:\n"
        stats_text += f"Мédiane: {stats['50%']:.2f}%\n"
        stats_text += f"Min: {stats['min']:.2f}%\n"
        stats_text += f"Max: {stats['max']:.2f}%\n"
    
    st.plotly_chart(fig4)
    st.text(stats_text)
    
    #5. Évolution du pourcentage de diplômés de l'enseignement supérieur par année
    st.subheader("Dynamique de l'enseignement supérieur")
    
    years = range(1945, 2023)
    avg_edu = []
    
    for year in years:
        if f'psup{year}' in diplomes_departements.columns:
            avg_edu.append(diplomes_departements[f'psup{year}'].mean())
    
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=list(years)[:len(avg_edu)],
        y=avg_edu,
        mode='lines+markers',
        name='Pourcentage moyen de personnes ayant fait des études supérieures'
    ))
    
    fig5.update_layout(
        title='Évolution du pourcentage de diplômés de l\'enseignement supérieur par année',
        xaxis_title='Année',
        yaxis_title='Pourcentage moyen',
        showlegend=True
    )
    st.plotly_chart(fig5)
    
   # 6. Nombre de diplômés par année
    st.subheader("Dynamique du nombre de diplômés")
    
    years = range(1945, 2023)
    total_diplomas = []
    men_diplomas = []
    women_diplomas = []
    
    for year in years:
        if all(f'{col}{year}' in diplomes_departements.columns for col in ['nodip', 'nodiph', 'nodipf']):
            total_diplomas.append(diplomes_departements[f'nodip{year}'].sum())
            men_diplomas.append(diplomes_departements[f'nodiph{year}'].sum())
            women_diplomas.append(diplomes_departements[f'nodipf{year}'].sum())
    
    fig6 = go.Figure()
    
    fig6.add_trace(go.Scatter(
        x=list(years)[:len(total_diplomas)],
        y=total_diplomas,
        mode='lines+markers',
        name='Nombre total de diplômés'
    ))
    
    fig6.add_trace(go.Scatter(
        x=list(years)[:len(men_diplomas)],
        y=men_diplomas,
        mode='lines+markers',
        name='Nombre de diplômés hommes'
    ))
    
    fig6.add_trace(go.Scatter(
        x=list(years)[:len(women_diplomas)],
        y=women_diplomas,
        mode='lines+markers',
        name='Nombre de diplômés femmes'
    ))
    
    fig6.update_layout(
        title='Dynamique du nombre de diplômés',
        xaxis_title='Année',
        yaxis_title='Nombre de diplômés',
        showlegend=True
    )
    st.plotly_chart(fig6)
    
    # 7. Évolution du pourcentage de réussite au baccalauréat par année
    st.subheader("Évolution du pourcentage de succès au baccalauréat par année")
    
    years = range(1945, 2023)
    bac_percent = []
    
    for year in years:
        if f'pbac{year}' in diplomes_departements.columns:
            bac_percent.append(diplomes_departements[f'pbac{year}'].mean())
    
    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=list(years)[:len(bac_percent)],
        y=bac_percent,
        mode='lines+markers',
        name='Pourcentage de succès au baccalauréat',
        line=dict(color='purple')
    ))
    
    fig7.update_layout(
        title='Évolution du pourcentage de succès au baccalauréat par année',
        xaxis_title='Année',
        yaxis_title='Pourcentage de succès au baccalauréat',
        showlegend=True
    )
    st.plotly_chart(fig7)
    
    # 8. Taux de réussite au baccalauréat par département
    st.subheader("Évolution du pourcentage de succès au baccalauréat par année par departement")
    
    fig8 = go.Figure()
    
    for _, row in diplomes_departements.iterrows():
        bac_values = []
        for year in years:
            if f'pbac{year}' in diplomes_departements.columns:
                bac_values.append(row[f'pbac{year}'])
        
        if bac_values:  # Vérifier qu'il y a des données
            fig8.add_trace(go.Scatter(
                x=list(years)[:len(bac_values)],
                y=bac_values,
                mode='lines',
                name=row['nomdep']
            ))
    
    fig8.update_layout(
        title='Évolution du pourcentage de succès au baccalauréat par année par departement',
        xaxis_title='Année',
        yaxis_title='Pourcentage de succès au baccalauréat',
        showlegend=True
    )
    st.plotly_chart(fig8)
    
    # Ajout d'un texte explicatif
    st.markdown("""
    ### Conclusions:
    
    1. **Correlation avec le vote**: Le graphique montre la corrélation entre le niveau d'education et le nombre de votes pour le candidat Melenchon.
    
    2. **Tendances par département**: Nous observons une tendance constante du niveau d'education dans les 5 départements les plus populaire.
    
    3. **Aspects généraux**: Le graphique montre l'histoire de la disparition du genre dans l'education.
    
    4. **Distribution par commune**: La histogramme montre la distribution du niveau d'education par commune.
    
   5. **Croissance de l’enseignement supérieur** : Le pourcentage de personnes titulaires d’un diplôme universitaire a augmenté régulièrement depuis 1945.

    6. **Équilibre entre les sexes** : Le graphique montre la répartition des diplômés par sexe, démontrant la dynamique historique de l'équilibre entre les sexes dans l'éducation.

    7. **Taux de succès au premier cycle** : Le taux de succès au premier cycle montre une augmentation constante, indiquant une amélioration de la qualité de l'enseignement secondaire.

    8. **Différences régionales** : L’analyse par département montre des différences significatives dans les taux de succès au baccalauréat entre les régions de France.
 """)