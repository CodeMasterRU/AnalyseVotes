import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

def calculate_percentage_for_year_superieurs(row, year):
    sup_col_men = f'suph{year}'
    sup_col_women = f'supf{year}'

    if sup_col_men in row and sup_col_women in row:
        total = row[sup_col_men] + row[sup_col_women]
        if total != 0:
            return (row[sup_col_men] + row[sup_col_women]) / total * 100
    return 0

def calculate_percentage_for_year_no_diplomes(row, year):
    nodip_col_men = f'nodiph{year}'
    nodip_col_women = f'nodipf{year}'

    if nodip_col_men in row and nodip_col_women in row:
        men_value = row.get(nodip_col_men, 0)
        women_value = row.get(nodip_col_women, 0)
        total = men_value + women_value
        if total > 0:
            return total
    return 0

def run1(diplomes_communes, diplomes_departements, pres_df):
    # Проверяем структуру данных
    st.write("### Structure des données initiales ###")
    st.write("Shape diplomes_communes:", diplomes_communes.shape)
    st.write("Shape diplomes_departements:", diplomes_departements.shape)
    st.write("Shape pres_df:", pres_df.shape)
    
    # Пример данных
    st.write("\nExemple diplomes_communes:")
    st.write(diplomes_communes.head())
    st.write("\nExemple diplomes_departements:")
    st.write(diplomes_departements.head())
    
    # Объединение данных по коммунам и департаментам
    merged_communes_df = pd.merge(diplomes_communes, pres_df, left_on='codecommune', right_on='codecommune')
    merged_departements_df = pd.merge(diplomes_departements, pres_df, left_on='nomdep', right_on='nomdep')
    
    st.write("\n### Structure après merge ###")
    st.write("Shape merged_communes:", merged_communes_df.shape)
    st.write("Shape merged_departements:", merged_departements_df.shape)
    
    # Проверяем колонки с данными о дипломах
    bac_cols_communes = [col for col in merged_communes_df.columns if 'bac' in col.lower()]
    nodip_cols_communes = [col for col in merged_communes_df.columns if 'nodip' in col.lower()]
    
    st.write("\n### Colonnes avec données sur les diplômes ###")
    st.write("Colonnes bac dans communes:", bac_cols_communes)
    st.write("Colonnes nodip dans communes:", nodip_cols_communes)
    
    # Проверяем данные в этих колонках
    st.write("\n### Statistiques des données ###")
    if bac_cols_communes:
        st.write("Statistiques bac communes:")
        st.write(merged_communes_df[bac_cols_communes].describe())
    
    if nodip_cols_communes:
        st.write("Statistiques nodip communes:")
        st.write(merged_communes_df[nodip_cols_communes].describe())
    
    # Определяем колонки для извлечения (бакалавриат)
    columns_to_extract_bac = ['nomdep_x', 'nomcommune_x'] + \
                     [f'pbac{year}' for year in range(1945, 2026)] + \
                     [f'pbacf{year}' for year in range(1945, 2026)] + \
                     [f'pbacm{year}' for year in range(1945, 2026)]

    # Колонки для людей без высшего образования
    columns_to_extract_no_diplomes = ['nomdep_x', 'nomcommune_x'] + \
                     [f'nodip{year}' for year in range(1945, 2026)] + \
                     [f'nodiph{year}' for year in range(1945, 2026)] + \
                     [f'nodipf{year}' for year in range(1945, 2026)]

    # Фильтруем колонки для коммун
    bac_columns_communes = [col for col in columns_to_extract_bac if col in merged_communes_df.columns]
    nodip_columns_communes = [col for col in columns_to_extract_no_diplomes if col in merged_communes_df.columns]

    # Фильтруем колонки для департаментов
    bac_columns_dept = [col for col in columns_to_extract_bac if col in merged_departements_df.columns]
    nodip_columns_dept = [col for col in columns_to_extract_no_diplomes if col in merged_departements_df.columns]

    # Выводим отладочную информацию
    st.write("Colonnes bac communes trouvées:", [col for col in bac_columns_communes if any(str(year) in col for year in range(1945, 2026))])
    st.write("Colonnes nodip communes trouvées:", [col for col in nodip_columns_communes if any(str(year) in col for year in range(1945, 2026))])
    
    # Извлекаем данные
    bac_communes = merged_communes_df[bac_columns_communes]
    nodip_communes = merged_communes_df[nodip_columns_communes]
    bac_dept = merged_departements_df[bac_columns_dept]
    nodip_dept = merged_departements_df[nodip_columns_dept]

    years = list(range(1945, 2026))

    # Функция для расчета процента с бакалавриатом
    def calculate_bac_percentage(df, is_commune=True):
        percentages = []
        for year in years:
            # Для каждого года берем все соответствующие колонки с правильными префиксами
            bac_cols = [col for col in df.columns if str(year) in col and ('bach' in col or 'bacf' in col or 'bacm' in col)]
            nodip_cols = [col for col in df.columns if str(year) in col and ('nodip' in col or 'nodiph' in col or 'nodipf' in col)]
            
            if bac_cols and nodip_cols:
                # Суммируем все значения бакалавров и без диплома для каждой строки
                bac_sum = df[bac_cols].sum(axis=1)
                total_sum = bac_sum + df[nodip_cols].sum(axis=1)
                
                # Вычисляем процент, избегая деления на 0
                percentage = (bac_sum / total_sum.replace(0, 1) * 100).mean()
                percentages.append(percentage if not pd.isna(percentage) else 0)
                
                # Выводим отладочную информацию для первого года с данными
                if len(percentages) == 1:
                    st.write(f"\nDébug bac année {year}:")
                    st.write("Colonnes bac trouvées:", bac_cols)
                    st.write("Colonnes nodip trouvées:", nodip_cols)
                    st.write("Somme bacheliers:", bac_sum.head())
                    st.write("Total:", total_sum.head())
                    st.write("Pourcentage:", percentage)
            else:
                percentages.append(0)
        return percentages

    # Функция для расчета процента без диплома
    def calculate_nodip_percentage(df, is_commune=True):
        percentages = []
        for year in years:
            # Для каждого года берем все соответствующие колонки с правильными префиксами
            bac_cols = [col for col in df.columns if str(year) in col and ('bach' in col or 'bacf' in col or 'bacm' in col)]
            nodip_cols = [col for col in df.columns if str(year) in col and ('nodip' in col or 'nodiph' in col or 'nodipf' in col)]
            
            if bac_cols and nodip_cols:
                # Суммируем все значения бакалавров и без диплома для каждой строки
                nodip_sum = df[nodip_cols].sum(axis=1)
                total_sum = nodip_sum + df[bac_cols].sum(axis=1)
                
                # Вычисляем процент, избегая деления на 0
                percentage = (nodip_sum / total_sum.replace(0, 1) * 100).mean()
                percentages.append(percentage if not pd.isna(percentage) else 0)
                
                # Выводим отладочную информацию для первого года с данными
                if len(percentages) == 1:
                    st.write(f"\nDébug nodip année {year}:")
                    st.write("Colonnes bac trouvées:", bac_cols)
                    st.write("Colonnes nodip trouvées:", nodip_cols)
                    st.write("Somme sans diplôme:", nodip_sum.head())
                    st.write("Total:", total_sum.head())
                    st.write("Pourcentage:", percentage)
            else:
                percentages.append(0)
        return percentages

    # Создаем графики
    st.subheader("Évolution du niveau d'éducation")
    
    # График для бакалавриата
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # Данные для коммун и департаментов
    bac_communes_pct = calculate_bac_percentage(bac_communes)
    bac_dept_pct = calculate_bac_percentage(bac_dept, False)
    
    # График бакалавриата
    ax1.plot(years, bac_communes_pct, label='Communes')
    ax1.plot(years, bac_dept_pct, label='Départements')
    ax1.set_title("Évolution du pourcentage de bacheliers")
    ax1.set_xlabel('Année')
    ax1.set_ylabel('Pourcentage (%)')
    ax1.legend()
    
    # Данные для без диплома
    nodip_communes_pct = calculate_nodip_percentage(nodip_communes)
    nodip_dept_pct = calculate_nodip_percentage(nodip_dept, False)
    
    # График без диплома
    ax2.plot(years, nodip_communes_pct, label='Communes')
    ax2.plot(years, nodip_dept_pct, label='Départements')
    ax2.set_title('Évolution du pourcentage de personnes sans diplôme')
    ax2.set_xlabel('Année')
    ax2.set_ylabel('Pourcentage (%)')
    ax2.legend()
    
    plt.tight_layout()
    st.pyplot(fig)

    # Таблицы с данными
    st.subheader("Données détaillées")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Données par commune")
        # Вычисляем средние значения для последнего года
        latest_year = max(years)
        
        # Получаем доступные колонки для последнего года
        bac_cols_latest = [col for col in bac_columns_communes if str(latest_year) in col]
        nodip_cols_latest = [col for col in nodip_columns_communes if str(latest_year) in col]
        
        communes_data = pd.DataFrame({
            'Commune': merged_communes_df['nomcommune_x'],
            'Département': merged_communes_df['nomdep_x'],
            'Bacheliers (%)': merged_communes_df[bac_cols_latest].mean(axis=1).round(2) if bac_cols_latest else 0,
            'Sans diplôme (%)': merged_communes_df[nodip_cols_latest].mean(axis=1).round(2) if nodip_cols_latest else 0
        })
        st.dataframe(communes_data.sort_values('Bacheliers (%)', ascending=False), height=400)
    
    with col2:
        st.write("Données par département")
        # Получаем доступные колонки для последнего года
        bac_cols_latest_dept = [col for col in bac_columns_dept if str(latest_year) in col]
        nodip_cols_latest_dept = [col for col in nodip_columns_dept if str(latest_year) in col]
        
        dept_data = pd.DataFrame({
            'Département': merged_departements_df['nomdep'],
            'Bacheliers (%)': merged_departements_df[bac_cols_latest_dept].mean(axis=1).round(2) if bac_cols_latest_dept else 0,
            'Sans diplôme (%)': merged_departements_df[nodip_cols_latest_dept].mean(axis=1).round(2) if nodip_cols_latest_dept else 0
        })
        st.dataframe(dept_data.sort_values('Bacheliers (%)', ascending=False), height=400)

    return bac_communes, nodip_communes, bac_dept, nodip_dept
