import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import json
import folium
from streamlit_folium import st_folium

def create_departement_map_with_pbac_labels(df_extracted, year):
    # Создаем базовую карту Франции
    m = folium.Map(location=[46.6034, 1.8883], zoom_start=5)

    # Загружаем GeoJSON с границами департаментов
    with open('GeoJson/departements_uppercase_fixed.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # Проверка наличия данных за указанный год
    if f'pbac{year}' not in df_extracted.columns:
        st.error(f"Данные за {year} отсутствуют!")
        return m

    # Подготовка данных для визуализации
    data_for_map = df_extracted[['nomdep', f'pbac{year}']].copy()
    data_for_map.set_index('nomdep', inplace=True)

    # Функция для окраски и показа подписей
    def style_function(feature):
        nomdep = feature['properties']['nomdep']
        pbac_value = data_for_map.loc[nomdep, f'pbac{year}'] if nomdep in data_for_map.index else 0
        return {
            'fillColor': 'YlGnBu',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        }

    # Добавление границ департаментов с подписями
    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["nomdep"],
            aliases=["Département: "],
            localize=True
        )
    ).add_to(m)

    # Добавляем текстовые метки с процентом сдачи
    for nomdep, row in data_for_map.iterrows():
        # Попытка найти координаты для департамента
        coord = next(
            (feature['geometry']['coordinates'][0][0] 
             for feature in geojson_data['features'] 
             if feature['properties']['nomdep'] == nomdep), None)

        # Проверка, найдены ли координаты
        if coord:
            # Если координаты многоугольные, берем центр первой области
            if isinstance(coord[0], list):
                lon, lat = coord[0][0], coord[0][1]  
            else:
                lon, lat = coord  
                
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=f"<div style='font-size: 10pt; color: black;'>{row[f'pbac{year}']}%</div>")
            ).add_to(m)
        else:
            st.warning(f"Координаты для {nomdep} не найдены!")

    # Легенда и контроль слоев
    folium.LayerControl().add_to(m)
    return m


def run1(diplomes_communes, diplomes_departements, pres_df):
    st.title("Graphique")
    st.write("Bienvenue sur info de diplomes!")

    diplomes_communes = diplomes_communes.rename(columns={'codecommune': 'code_commune'})
    pres_df = pres_df.rename(columns={'codecommune': 'code_commune'})
    merged_df = pd.merge(pres_df, diplomes_communes, on='code_commune', how='inner')
    columns_to_extract = ['nomdep'] + \
                     [f'palpha{year}' for year in range(1945, 2026)] + \
                     [f'palphah{year}' for year in range(1945, 2026)] + \
                     [f'palphaf{year}' for year in range(1945, 2026)] + \
                     [f'nodip{year}' for year in range(1945, 2026)] + \
                     [f'nodiph{year}' for year in range(1945, 2026)] + \
                     [f'nodipf{year}' for year in range(1945, 2026)] + \
                     [f'bac{year}' for year in range(1945, 2026)] + \
                     [f'bach{year}' for year in range(1945, 2026)] + \
                     [f'bacf{year}' for year in range(1945, 2026)] + \
                     [f'pbac{year}' for year in range(1945, 2026)] + \
                     [f'sup{year}' for year in range(1945, 2026)] + \
                     [f'suph{year}' for year in range(1945, 2026)] + \
                     [f'supf{year}' for year in range(1945, 2026)] + \
                     [f'psup{year}' for year in range(1945, 2026)]

    # Фильтруем только те колонки, которые есть в данных
    columns_to_extract_existing = [col for col in columns_to_extract if col in diplomes_departements.columns]

    # Извлекаем только существующие колонки
    df_extracted = diplomes_departements[columns_to_extract_existing]
    years = list(range(1945, 2026))

    # Fonction pour calculer le pourcentage de personnes ayant fait des études supérieures pendant un an
    def calculate_percentage_for_year(row, year):
        sup_col_men = f'suph{year}'
        sup_col_women = f'supf{year}'
        nodip_col_men = f'nodiph{year}'
        nodip_col_women = f'nodipf{year}'

        if sup_col_men in row and sup_col_women in row and nodip_col_men in row and nodip_col_women in row:
            total = row[nodip_col_men] + row[nodip_col_women] + row[sup_col_men] + row[sup_col_women]
        
            if total != 0:
                return (row[sup_col_men] + row[sup_col_women]) / total * 100
            else:
                return 0
        else:
            return 0

    # Appliquer le calcul pour chaque année et résumer les résultats
    merged_df['percent_high_edu'] = merged_df.apply(
        lambda row: sum(
            calculate_percentage_for_year(row, year) for year in years
        ) / len(years), axis=1
    )
    print(merged_df.columns)


    candidates = [
        'ROUSSEL', 'ARTHAUD', 'POUTOU', 'MELENCHON', 'JADOT', 'HIDALGO', 'LASSALLE', 'MACRON', 'PECRESSE', 'ZEMMOUR', 'DUPONTAIGNAN', 'MLEPEN'
    ]

    selected_candidate = st.selectbox('Sélectionnez un candidat :', candidates)

    def get_correlation(candidate):
        candidate_col = f'voix{candidate}'
        if candidate_col in merged_df.columns:
            correlation = merged_df[['percent_high_edu', candidate_col]].corr()
            return correlation.iloc[0, 1]
        else:
            return None


    correlation_value = get_correlation(selected_candidate)
    if correlation_value is not None:
        st.write(f'Corrélation entre le niveau d’éducation et les votes pour {selected_candidate}: {correlation_value}')
    else:
        st.write(f'Données pour le candidat {selected_candidate} pas trouvé.')

    st.write('Tableau de données avec le pourcentage de personnes ayant fait des études supérieures :')
    st.dataframe(merged_df[['nomcommune_x', 'percent_high_edu']])

    st.write('Les données sur les élections et le niveau d’éducation ont été combinées par code communal.')
    st.write("La valeur de corrélation entre le niveau d'éducation et les votes est affichée pour chaque candidat.")
    return df_extracted
