import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def run_diplomes(diplomes_communes, diplomes_departements, pres_df, leg_df=None):
    st.title("Analyse du niveau d'éducation en France")
    
    # Добавляем новую секцию для таблицы данных
    st.subheader("Données détaillées par commune et département")

    # Добавляем выбор года
    years = [str(year) for year in range(2010, 2023)]
    selected_year = st.sidebar.selectbox(
        "Sélectionnez l'année pour l'analyse",
        years
    )

    # Проверяем наличие необходимых колонок
    required_columns = [
        f'suph{selected_year}', f'supf{selected_year}',
        f'bach{selected_year}', f'bacf{selected_year}',
        f'nodiph{selected_year}', f'nodipf{selected_year}'
    ]

    if not all(col in diplomes_communes.columns for col in required_columns):
        st.error(f"Données non disponibles pour l'année {selected_year}")
        return

    tab_communes, tab_departements = st.tabs(["Communes", "Départements"])
    
    with tab_communes:
        try:
            # Подготовка данных для коммун
            communes_data = diplomes_communes.copy()
            communes_data['total_diplomes'] = (
                communes_data[f'suph{selected_year}'].fillna(0) + 
                communes_data[f'supf{selected_year}'].fillna(0) + 
                communes_data[f'bach{selected_year}'].fillna(0) + 
                communes_data[f'bacf{selected_year}'].fillna(0)
            )
            communes_data['total_sans_diplome'] = (
                communes_data[f'nodiph{selected_year}'].fillna(0) + 
                communes_data[f'nodipf{selected_year}'].fillna(0)
            )
            
            # Безопасный расчет процента
            total = communes_data['total_diplomes'] + communes_data['total_sans_diplome']
            communes_data['pourcentage_diplomes'] = np.where(
                total > 0,
                (communes_data['total_diplomes'] / total * 100).round(2),
                0
            )

            # Подготовка данных для отображения
            # Для коммун
            communes_display = communes_data[['nomcommune', 'nomdep', 'total_diplomes', 
                                           'pourcentage_diplomes', 'total_sans_diplome']]
            communes_display.columns = ['Commune', 'Département', 'Total Diplômés', 
                                      'Pourcentage Diplômés (%)', 'Sans Diplôme']

            # Поиск по коммунам
            search_commune = st.text_input("Rechercher une commune:")
            if search_commune:
                filtered_communes = communes_display[
                    communes_display['Commune'].str.contains(search_commune, case=False, na=False)
                ]
                st.dataframe(filtered_communes, use_container_width=True)
            else:
                st.dataframe(communes_display, use_container_width=True)

        except Exception as e:
            st.error(f"Erreur lors du traitement des données communes: {str(e)}")

    with tab_departements:
        try:
            # Подготовка данных для департаментов
            dept_data = diplomes_departements.copy()
            dept_data['total_diplomes'] = (
                dept_data[f'sup{selected_year}'].fillna(0) + 
                dept_data[f'bac{selected_year}'].fillna(0)
            )
            dept_data['total_sans_diplome'] = dept_data[f'nodip{selected_year}'].fillna(0)
            
            # Безопасный расчет процента
            total = dept_data['total_diplomes'] + dept_data['total_sans_diplome']
            dept_data['pourcentage_diplomes'] = np.where(
                total > 0,
                (dept_data['total_diplomes'] / total * 100).round(2),
                0
            )

            # Подготовка данных для отображения
            dept_display = dept_data[['nomdep', 'total_diplomes', 'pourcentage_diplomes', 'total_sans_diplome']]
            dept_display.columns = ['Département', 'Total Diplômés', 'Pourcentage Diplômés (%)', 'Sans Diplôme']

            # Поиск по департаментам
            search_dept = st.text_input("Rechercher un département:")
            if search_dept:
                filtered_depts = dept_display[
                    dept_display['Département'].str.contains(search_dept, case=False, na=False)
                ]
                st.dataframe(filtered_depts, use_container_width=True)
            else:
                st.dataframe(dept_display, use_container_width=True)

        except Exception as e:
            st.error(f"Erreur lors du traitement des données départements: {str(e)}")

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
        if leg_df is not None:
            election_df = leg_df
            vote_columns = [col for col in leg_df.columns if col.startswith('voix')]
            candidates = [col[4:] for col in vote_columns]
        else:
            st.error("Les données des élections législatives ne sont pas disponibles")
            return
    
    # 1. Объединение данных о дипломах и выборах
    merged_df = pd.merge(election_df, diplomes_communes, on='codecommune', how='inner')

    # Добавление переменной процента людей с высшим образованием
    sup_h_col = f'suph{selected_year}'
    sup_f_col = f'supf{selected_year}'
    nodip_h_col = f'nodiph{selected_year}'
    nodip_f_col = f'nodipf{selected_year}'

    # Заменяем NaN и Inf значения на 0 и проверяем деление на 0
    merged_df[sup_h_col] = merged_df[sup_h_col].replace([np.inf, -np.inf], 0).fillna(0)
    merged_df[sup_f_col] = merged_df[sup_f_col].replace([np.inf, -np.inf], 0).fillna(0)
    merged_df[nodip_h_col] = merged_df[nodip_h_col].replace([np.inf, -np.inf], 0).fillna(0)
    merged_df[nodip_f_col] = merged_df[nodip_f_col].replace([np.inf, -np.inf], 0).fillna(0)
    
    # Исправляем расчет процента людей с высшим образованием
    total_population = (
        merged_df[sup_h_col] + merged_df[sup_f_col] +  # люди с высшим образованием
        merged_df[nodip_h_col] + merged_df[nodip_f_col]  # люди без высшего образования
    )
    
    merged_df['percent_high_edu'] = np.where(
        total_population > 0,
        ((merged_df[sup_h_col] + merged_df[sup_f_col]) / total_population * 100).round(2),
        0
    )
    
    # Удаляем аномальные значения
    merged_df = merged_df[merged_df['percent_high_edu'] <= 100]
    
    # 2. Фильтрация данных по выбранному году
    st.subheader(f"Analyse du niveau d'éducation pour l'année {selected_year}")
    
    # Фильтруем данные по выбранному году
    selected_year_col = f'psup{selected_year}'
    if selected_year_col in diplomes_communes.columns:
        st.write(f"Affichage des données pour l'année {selected_year}:")
    else:
        st.error(f"Les données pour l'année {selected_year} ne sont pas disponibles.")
        return

    # 3. Создание графиков
    # Сначала добавляем вкладки для анализа
    tab1, tab2, tab3 = st.tabs(["Graphique de dispersion", "Matrice de correlation", "Graphique suplementaire"])
    
    with tab1:
        # Позволяем пользователю выбрать кандидата/партию для анализа
        selected_candidate = st.selectbox(
            "Choisissez un candidat/parti pour analyser",
            range(len(candidates)),
            format_func=lambda x: candidates[x]
        )
        
        # График рассеяния для выбранного кандидата/партии
        fig1 = px.scatter(merged_df, 
                         x='percent_high_edu', 
                         y=vote_columns[selected_candidate],
                         title=f'Correlation entre le niveau d\'education et les votes pour {candidates[selected_candidate]} ({election_type})',
                         labels={'percent_high_edu': 'Pourcentage de personnes avec un niveau d\'education supérieur (%)',
                                vote_columns[selected_candidate]: f'Nombre de votes pour {candidates[selected_candidate]}'} )
        
        # Добавляем линию тренда
        fig1.add_traces(
            px.scatter(merged_df, 
                      x='percent_high_edu', 
                      y=vote_columns[selected_candidate],
                      trendline="ols").data[1]
        )
        st.plotly_chart(fig1)
        
        # Вычисляем и отображаем коэффициент корреляции
        correlation = merged_df['percent_high_edu'].corr(merged_df[vote_columns[selected_candidate]])
        st.write(f"Coef de correlation: {correlation:.3f}")
        
    with tab2:
        # Создание матрицы корреляций
        corr_data = merged_df[['percent_high_edu'] + vote_columns].corr()
        
        # Создаем тепловую карту для матрицы корреляции
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
        # Дополнительные графики
        st.subheader("Graphiques supplémentaires")
        fig3 = plt.figure(figsize=(10, 6))
        plt.plot(merged_df['codecommune'], merged_df['percent_high_edu'], label='Niveau d\'education')
        plt.xlabel('Code de la commune')
        plt.ylabel('Pourcentage de personnes avec un niveau d\'education supérieur (%)')
        plt.title(f"Pourcentage de l'enseignement supérieur par commune en {selected_year}")
        plt.legend()
        st.pyplot(fig3)
    




    # 4. Анализ по департаментам
    st.subheader(f"Tendances de l'éducation par département en {selected_year}")

    # Получаем топ-5 департаментов по уровню образования за выбранный год
    top_deps = diplomes_departements.nlargest(5, selected_year_col)[['nomdep', selected_year_col]]

    # Создаем barplot
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=top_deps['nomdep'], 
        y=top_deps[selected_year_col], 
        text=top_deps[selected_year_col].round(2), 
        textposition='auto',
        marker=dict(color='blue')
    ))

    # Обновляем оформление графика
    fig.update_layout(
        title=f'Top-5 départements par niveau d\'éducation ({selected_year})',
        xaxis_title='Département',
        yaxis_title='Pourcentage de personnes avec un niveau d\'education supérieur (%)',
        hovermode='x'
    )

    st.plotly_chart(fig)










# Tendances de l'éducation par département
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
    
    # 5. Генерация графиков для анализа по полу
    st.subheader("Génère un graphique des tendances de l'education par sexe")
    
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
                   title=f"Inégalités entre les sexes dans l'enseignement supérieur ({selected_year})",
                   labels={'value': 'Moyenne des personnes avec un niveau d\'education supérieur (%)',
                          'variable': 'Sexe'})
    st.plotly_chart(fig3)
    
    # Add correlation analysis here (inside the run_diplomes function)
    st.header("Analyse de corrélation entre l'éducation et les votes")

    try:
        # Prepare education and voting data
        education_voting_data = pd.DataFrame()
        
        # Безопасно добавляем информацию о коммуне
        if 'nomcommune' in merged_df.columns:
            education_voting_data['commune'] = merged_df['nomcommune']
        elif 'commune' in merged_df.columns:
            education_voting_data['commune'] = merged_df['commune']
        else:
            education_voting_data['commune'] = merged_df.index
            
        # Безопасно добавляем информацию о департаменте
        if 'nomdep' in merged_df.columns:
            education_voting_data['departement'] = merged_df['nomdep']
        elif 'departement' in merged_df.columns:
            education_voting_data['departement'] = merged_df['departement']
        else:
            education_voting_data['departement'] = 'Non spécifié'

        # Calculate education percentages
        total_education = (
        merged_df[f'suph{selected_year}'] + 
        merged_df[f'supf{selected_year}'] + 
        merged_df[f'bach{selected_year}'] + 
        merged_df[f'bacf{selected_year}'] + 
        merged_df[f'nodiph{selected_year}'] + 
        merged_df[f'nodipf{selected_year}']
        ).replace(0, np.nan)

        education_voting_data['pct_superior'] = (
        (merged_df[f'suph{selected_year}'] + merged_df[f'supf{selected_year}']) / total_education * 100
        ).fillna(0)

        education_voting_data['pct_bac'] = (
        (merged_df[f'bach{selected_year}'] + merged_df[f'bacf{selected_year}']) / total_education * 100
        ).fillna(0)

        education_voting_data['pct_nodip'] = (
        (merged_df[f'nodiph{selected_year}'] + merged_df[f'nodipf{selected_year}']) / total_education * 100
        ).fillna(0)

        # Add voting data with percentages instead of absolute numbers
        total_votes = sum(merged_df[col] for col in vote_columns)
        for col in vote_columns:
            education_voting_data[col] = (merged_df[col] / total_votes * 100).fillna(0)

        # Create correlation analysis tabs
        corr_tab1, corr_tab2 = st.tabs(["Graphiques de corrélation", "Matrice de corrélation"])

        with corr_tab1:
            # Select candidate/party for analysis
            vote_cols = [col for col in education_voting_data.columns if col.startswith('voix')]
            selected_candidate = st.selectbox(
            "Sélectionnez un candidat/parti pour l'analyse de corrélation",
            vote_cols,
            format_func=lambda x: x[4:]
            )

        # Create scatter plots
        fig_sup = px.scatter(education_voting_data, 
        x='pct_superior', 
        y=selected_candidate,
        trendline="ols",
        title=f"Corrélation: Niveau supérieur et votes pour {selected_candidate[4:]}",
        labels={
        'pct_superior': '% Éducation supérieure',
        selected_candidate: 'Nombre de votes'
        }
        )
        
        # Улучшаем читаемость графика
        fig_sup.update_layout(
            xaxis_range=[0, 100],  # Ограничиваем процент от 0 до 100
            showlegend=True,
            height=600,
            width=800
        )
        
        # Добавляем подписи точек при наведении
        fig_sup.update_traces(
            hovertemplate="<br>".join([
                "Commune: %{text}",
                "% Education supérieure: %{x:.1f}%",
                "Votes: %{y}"
            ]),
            text=education_voting_data['commune']
        )
        st.plotly_chart(fig_sup)

        # Calculate and display correlation coefficients
        corr_sup = education_voting_data['pct_superior'].corr(education_voting_data[selected_candidate])
        corr_bac = education_voting_data['pct_bac'].corr(education_voting_data[selected_candidate])
        corr_nodip = education_voting_data['pct_nodip'].corr(education_voting_data[selected_candidate])

        st.write(f"Coefficients de corrélation pour {selected_candidate[4:]}:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Niveau supérieur", f"{corr_sup:.3f}")
        with col2:
            st.metric("Niveau Bac", f"{corr_bac:.3f}")
        with col3:
            st.metric("Sans diplôme", f"{corr_nodip:.3f}")

        with corr_tab2:
            # Create correlation matrix only for education levels and votes
            education_cols = ['pct_superior', 'pct_bac', 'pct_nodip']
            corr_matrix = pd.DataFrame()
            
            # Calculate correlations between education and votes
            for edu_col in education_cols:
                correlations = []
                for vote_col in vote_cols:
                    corr = education_voting_data[edu_col].corr(education_voting_data[vote_col])
                    correlations.append(corr)
                corr_matrix[edu_col] = correlations
            
            corr_matrix.index = [col[4:] for col in vote_cols]  # Remove 'voix' prefix
            corr_matrix.columns = ['Niveau supérieur', 'Niveau Bac', 'Sans diplôme']
            
            # Create heatmap with better layout
            fig_matrix = px.imshow(
                corr_matrix,
                labels=dict(color="Correlation"),
                color_continuous_scale="RdBu_r",
                title="Corrélation entre niveaux d'éducation et votes par candidat",
                aspect="auto"  # Adjust aspect ratio
            )
            
            # Improve layout
            fig_matrix.update_layout(
                xaxis_title="Niveau d'éducation",
                yaxis_title="Candidats",
                width=800,
                height=600
            )
            
            st.plotly_chart(fig_matrix)
        
        # Move all the code up to the final st.plotly_chart(fig_matrix) here
        
    except Exception as e:
        st.error(f"Erreur lors de l'analyse de corrélation: {str(e)}")

        # Remove all the correlation analysis code that was here at the module level
        
        # После вывода коэффициентов корреляции
        def get_correlation_interpretation(corr):
            if abs(corr) < 0.1:
                return "Corrélation très faible ou inexistante"
            elif abs(corr) < 0.3:
                return "Corrélation faible"
            else:
                return "Corrélation modérée"
                
        st.write("### Interprétation des corrélations")
        for coef, level in [(corr_sup, "supérieur"), (corr_bac, "bac"), (corr_nodip, "sans diplôme")]:
            st.write(f"- Niveau {level}: {coef:.3f} - {get_correlation_interpretation(coef)}")
