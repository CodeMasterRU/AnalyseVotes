import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

@st.cache_data
def prepare_national_data(alpha_df):
    # Подготовка данных для национальной статистики
    sign_columns = [col for col in alpha_df.columns if col.startswith('conjsign')]
    nosi_columns = [col for col in alpha_df.columns if col.startswith('conjnosi')]
    
    sign_data = {}
    nosign_data = {}
    
    for col in sign_columns:
        year = col.replace('conjsign', '')
        sign_data[year] = alpha_df[col].mean()
    
    for col in nosi_columns:
        year = col.replace('conjnosi', '')
        nosign_data[year] = alpha_df[col].mean()
    
    return sign_data, nosign_data

def run_detailed_analysis(alpha_df):
    try:
        st.title("Analyse détaillée par département et commune")
        
        # Создаем селекторы для департамента и коммуны
        departments = sorted(alpha_df['nomdep'].unique())
        selected_dep = st.selectbox("Sélectionnez un département", departments)
        
        # Фильтруем коммуны по выбранному департаменту
        communes = sorted(alpha_df[alpha_df['nomdep'] == selected_dep]['nomcommune'].unique())
        selected_commune = st.selectbox("Sélectionnez une commune", communes)
        
        # Получаем данные для выбранной коммуны
        commune_data = alpha_df[
            (alpha_df['nomdep'] == selected_dep) & 
            (alpha_df['nomcommune'] == selected_commune)
        ]
        
        if commune_data.empty:
            st.error("Aucune donnée trouvée pour cette commune")
            return
            
        commune_data = commune_data.iloc[0]
        
        # Отображаем информационные карточки
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Code commune", commune_data['codecommune'])
        with col2:
            st.metric("Code département", commune_data['dep'])
        with col3:
            # Вычисляем средний уровень алфабетизации за последний доступный год
            latest_year = max([int(col.replace('peralpha', '')) 
                             for col in commune_data.index 
                             if col.startswith('peralpha')])
            latest_alpha = commune_data[f'peralpha{latest_year}']
            st.metric("Dernier taux d'alphabétisation", 
                     f"{latest_alpha:.1f}%",
                     f"Année {latest_year}")
        
        # Создаем график исторической динамики
        tab1, tab2, tab3 = st.tabs(["Évolution historique", "Comparaison départementale", "Évolution nationale"])
        
        with tab1:
            years = range(1816, 1947)
            historical_data = {
                'year': [],
                'percentage': []
            }
            
            for year in years:
                col_name = f'peralpha{year}'
                if col_name in commune_data.index and not pd.isna(commune_data[col_name]):
                    historical_data['year'].append(year)
                    historical_data['percentage'].append(commune_data[col_name])
            
            if historical_data['year']:
                fig = px.line(
                    historical_data,
                    x='year',
                    y='percentage',
                    title=f"Évolution historique du taux d'alphabétisation à {selected_commune}",
                    labels={'percentage': "Taux d'alphabétisation (%)", 'year': 'Année'}
                )
                fig.update_layout(
                    hovermode='x unified',
                    showlegend=True,
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Добавляем статистику изменений
                total_change = historical_data['percentage'][-1] - historical_data['percentage'][0]
                st.metric(
                    "Progression totale",
                    f"{total_change:.1f}%",
                    f"De {historical_data['year'][0]} à {historical_data['year'][-1]}"
                )
        
        with tab2:
            year_comparison = st.slider(
                "Sélectionnez l'année pour la comparaison", 
                1816, 1946, 
                1900
            )
            comparison_col = f'peralpha{year_comparison}'
            
            dep_data = alpha_df[alpha_df['nomdep'] == selected_dep].copy()
            
            # Добавляем базовую статистику
            mean_alpha = dep_data[comparison_col].mean()
            median_alpha = dep_data[comparison_col].median()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Moyenne départementale", f"{mean_alpha:.1f}%")
            with col2:
                st.metric("Médiane départementale", f"{median_alpha:.1f}%")
            
            # Улучшенный box plot
            fig2 = go.Figure()
            fig2.add_trace(go.Box(
                y=dep_data[comparison_col],
                name=selected_dep,
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8
            ))
            
            # Добавляем точку для выбранной коммуны
            fig2.add_trace(
                go.Scatter(
                    x=[selected_dep],
                    y=[commune_data[comparison_col]],
                    mode='markers',
                    name=selected_commune,
                    marker=dict(size=12, color='red', symbol='star')
                )
            )
            
            fig2.update_layout(
                title=f"Distribution du taux d'alphabétisation dans {selected_dep} ({year_comparison})",
                yaxis_title="Taux d'alphabétisation (%)",
                showlegend=True,
                height=500
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # Добавляем ранг коммуны
            commune_rank = dep_data[comparison_col].rank(ascending=False)
            commune_rank = commune_rank[dep_data['nomcommune'] == selected_commune].iloc[0]
            total_communes = len(dep_data)
            
            st.metric(
                "Rang de la commune",
                f"{int(commune_rank)} sur {total_communes}",
                f"Top {(commune_rank/total_communes*100):.1f}%"
            )
            
        with tab3:
            st.subheader("Évolution des indicateurs d'alphabétisation en France")
            
            # Подготовка данных для подписей
            sign_columns = [col for col in alpha_df.columns if col.startswith('conjsign')]
            nosi_columns = [col for col in alpha_df.columns if col.startswith('conjnosi')]
            
            sign_data = {}
            nosign_data = {}
            
            for col in sign_columns:
                year = col.replace('conjsign', '')
                sign_data[year] = alpha_df[col].mean()
            
            for col in nosi_columns:
                year = col.replace('conjnosi', '')
                nosign_data[year] = alpha_df[col].mean()
            
            # График для подписывающих/неподписывающих
            fig_sign = go.Figure()
            fig_sign.add_trace(go.Scatter(
                x=list(sign_data.keys()),
                y=list(sign_data.values()),
                name='Personnes sachant signer',
                mode='lines+markers'
            ))
            fig_sign.add_trace(go.Scatter(
                x=list(nosign_data.keys()),
                y=list(nosign_data.values()),
                name='Personnes ne sachant pas signer',
                mode='lines+markers'
            ))
            
            fig_sign.update_layout(
                title="Évolution de la capacité à signer (moyenne nationale)",
                xaxis_title="Année",
                yaxis_title="Nombre moyen de personnes",
                height=500
            )
            st.plotly_chart(fig_sign, use_container_width=True)
            
            # График для процента алфабетизации
            years_alpha = range(1816, 1947)
            alpha_means = {
                'year': [],
                'palpha': [],
                'peralpha': []
            }
            
            for year in years_alpha:
                if f'palpha{year}' in alpha_df.columns and f'peralpha{year}' in alpha_df.columns:
                    alpha_means['year'].append(year)
                    alpha_means['palpha'].append(alpha_df[f'palpha{year}'].mean())
                    alpha_means['peralpha'].append(alpha_df[f'peralpha{year}'].mean())
            
            fig_alpha = go.Figure()
            fig_alpha.add_trace(go.Scatter(
                x=alpha_means['year'],
                y=alpha_means['palpha'],
                name='Nombre alphabétisés',
                mode='lines+markers'
            ))
            fig_alpha.add_trace(go.Scatter(
                x=alpha_means['year'],
                y=alpha_means['peralpha'],
                name='Pourcentage alphabétisation',
                mode='lines+markers'
            ))
            
            fig_alpha.update_layout(
                title="Évolution de l'alphabétisation en France (1816-1946)",
                xaxis_title="Année",
                yaxis_title="Valeur moyenne",
                height=500
            )
            st.plotly_chart(fig_alpha, use_container_width=True)
            
            # Добавляем статистику изменений
            col1, col2 = st.columns(2)
            with col1:
                years_sign = sorted(list(sign_data.keys()))
                first_year = years_sign[0]
                last_year = years_sign[-1]
                sign_change = ((sign_data[last_year] - sign_data[first_year]) / sign_data[first_year] * 100)
                st.metric(
                    f"Évolution capacité à signer ({first_year}-{last_year})",
                    f"{sign_change:.1f}%"
                )
            with col2:
                alpha_change = alpha_means['peralpha'][-1] - alpha_means['peralpha'][0]
                st.metric(
                    "Évolution taux d'alphabétisation (1816-1946)",
                    f"{alpha_change:.1f}%"
                )
        
        # Delete everything below this point until the except statement
    except Exception as e:
        st.error(f"Une erreur s'est produite: {str(e)}")