import pandas as pd
import streamlit as st
import logging
import App.app1, App.app2, App.app3
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Data Visualization", layout="wide")
logging.basicConfig(level=logging.INFO)

st.title("🌍 DATAVISUALISATION")

selected = option_menu(
    menu_title=None,
    options=["Carte interactive", "Capital_immobilier", "Diplomes"],
    icons=["map", "bar-chart", "book"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

@st.cache_data
def load_data():
    try:
        data_files = {
            "agesexcommunes": "./Data/Age_csp/agesexcommunes.csv",
            "agesexdepartements": "./Data/Age_csp/agesexdepartements.csv",
            "alphabetisation": "./Data/Alphabetisation/alphabetisationcommunes.csv",
            "pres_df": "./Data/Elections_csv/Pres2022.csv",
            "leg_df": "./Data/Elections_csv/Legis2022.csv",
            "basesfiscalcommune": "./Data/Capital_immobilier_csv/basesfiscalescommunes.csv",
            "basesfiscaldepartement": "./Data/Capital_immobilier_csv/basesfiscalesdepartements.csv",
            "capitalimmobilier": "./Data/Capital_immobilier_csv/capitalimmobilier.csv",
            "capitalimmobiliercommune": "./Data/Capital_immobilier_csv/capitalimmobiliercommunes.csv",
            "capitalimmobilierdepartement": "./Data/Capital_immobilier_csv/capitalimmobilierdepartements.csv",
            "isfcommunes": "./Data/Capital_immobilier_csv/isfcommunes.csv",
            "terrescommunes": "./Data/Capital_immobilier_csv/terrescommunes.csv",
            "diplomes_communes": "./Data/Diplomes_csv/diplomescommunes.csv",
            "diplomes_departements": "./Data/Diplomes_csv/diplomesdepartements.csv",
        }

        data = {key: pd.read_csv(path, low_memory=False) for key, path in data_files.items()}
        return data
    except Exception as e:
        logging.error(f"Erreur lors du chargement des données: {e}")
        return None

data = load_data()
if data:
    locals().update(data)
else:
    st.error("Impossible de charger les données.")
    st.stop()

if selected == "Carte interactive":
    st.session_state.page = 'Carte interactive'
    App.app1.run_elections(data["pres_df"], data["leg_df"])
elif selected == "Capital_immobilier":
    st.session_state.page = 'Capital_immobilier'
    App.app2.run_immobilier(
        basesfiscalcommune=data["basesfiscalcommune"],
        basesfiscaldepartement=data["basesfiscaldepartement"],
        capitalimmobilier=data["capitalimmobilier"],
        capitalimmobiliercommune=data["capitalimmobiliercommune"],
        capitalimmobilierdepartement=data["capitalimmobilierdepartement"],
        isfcommunes=data["isfcommunes"],
        terrescommunes=data["terrescommunes"]
    )
elif selected == "Diplomes":
    st.session_state.page = 'Diplomes'
    App.app3.run_diplomes(
        diplomes_communes=data["diplomes_communes"],
        diplomes_departements=data["diplomes_departements"],
        pres_df=data["pres_df"],
        leg_df=data["leg_df"]
    )
