import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Функция для подготовки данных по образованию
def prepare_education_data(diplomes_communes, diplomes_departements, pres_df, leg_df=None):
    # 1. Объединение данных о дипломах и выборах
    merged_df = pd.merge(pres_df, diplomes_communes, on='codecommune', how='inner')
    merged_df['percent_high_edu'] = (merged_df['suph1962'] + merged_df['supf1962']) / (merged_df['nodiph1962'] + merged_df['nodipf1962']) * 100
    return merged_df

# Функция для вычисления корреляции
def plot_correlation(merged_df, vote_columns, candidates, election_type):
    st.subheader(f"Correlation entre le niveau d'éducation et les votes ({election_type})")
    
    if len(vote_columns) > 0:
        # Создаем вкладки для разных визуализаций
        tab1, tab2, tab3 = st.tabs(["Graphique de dispersion", "Matrice de correlation", "Graphique suplementaire"])
        
        with tab1:
            selected_candidate = st.selectbox(
                "Choisissez un candidat/parti pour analyser",
                range(len(candidates)),
                format_func=lambda x: candidates[x]
            )
            
            # График рассеяния
            fig1 = px.scatter(merged_df, 
                             x='percent_high_edu', 
                             y=vote_columns[selected_candidate],
                             title=f'Correlation entre le niveau d\'education et les votes pour {candidates[selected_candidate]} ({election_type})',
                             labels={'percent_high_edu': 'Pourcentage de personnes avec un niveau d\'education supérieur (%)',
                                    vote_columns[selected_candidate]: f'Nombre de votes pour {candidates[selected_candidate]}'})
            
            # Добавление линии тренда
            fig1.add_traces(
                px.scatter(merged_df, 
                          x='percent_high_edu', 
                          y=vote_columns[selected_candidate],
                          trendline="ols").data[1]
            )
            st.plotly_chart(fig1)
            
            # Коэффициент корреляции
            correlation = merged_df['percent_high_edu'].corr(merged_df[vote_columns[selected_candidate]])
            st.write(f"Coef de correlation: {correlation:.3f}")
            
        with tab2:
            # Матрица корреляции
            corr_data = merged_df[['percent_high_edu'] + vote_columns].corr()
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
            # Дополнительный график
            st.subheader("Graphiques supplémentaires")
            fig3 = plt.figure(figsize=(10, 6))
            plt.plot(merged_df['codecommune'], merged_df['percent_high_edu'], label='Niveau d\'education')
            plt.xlabel('Code de la commune')
            plt.ylabel('Pourcentage de personnes avec un niveau d\'education supérieur (%)')
            plt.title("Pourcentage de l'enseignement supérieur par commune")
            plt.legend()
            st.pyplot(fig3)
    
    else:
        st.error("Il n'y a aucune donnée de vote dans l'ensemble de données sélectionné.")

# Функция для трендов по департаментам
def plot_education_trends(diplomes_departements):
    st.subheader("Tendances de l'education par département")
    top_deps = diplomes_departements.nlargest(5, 'psup2022')[['nomdep', 'psup2022']]
    
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

# Основная функция для страницы
def run_diplomes(diplomes_communes, diplomes_departements, pres_df, leg_df=None):
    st.title("Analyse du niveau d'éducation en France")
    
    # Выводим названия колонок для отладки
    st.write("Disponibilités de colonnes dans les données des élections:")
    st.write(pres_df.columns.tolist())
    
    # Добавляем выбор типа выборов
    election_type = st.sidebar.radio("Sélectionnez le type d'élection", ('Présidentielle', 'Législative'))
    
    # Подготовим данные для анализа
    if election_type == 'Présidentielle':
        election_df = pres_df
    elif leg_df is not None:
        election_df = leg_df
    else:
        st.error("Les données des élections législatives ne sont pas disponibles")
        return
    
    # Подготовим данные об образовании
    merged_df = prepare_education_data(diplomes_communes, diplomes_departements, election_df)
    
    # Получаем список колонок голосования и имена кандидатов
    vote_columns = [col for col in election_df.columns if col.startswith('voix')]
    candidates = [col[4:] for col in vote_columns]
    
    # Анализ корреляции
    plot_correlation(merged_df, vote_columns, candidates, election_type)
    
    # Тренды по департаментам
    plot_education_trends(diplomes_departements)
    
    # Генерация графиков по образованию по годам и по полу
    st.subheader("Génère un graphique des tendances de l'éducation par sexe")
    gender_gap_data = {'Année': [], 'Hommes': [], 'Femmes': []}
    years_gender = range(1945, 1963)
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
    
    # Дополнительные визуализации и тренды...
    # (Твоя оставшаяся логика для других трендов)

