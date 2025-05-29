import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Configuration de l'application
st.set_page_config(
    page_title="Forex & Or en Temps Réel",
    page_icon="💹",
    layout="wide"
)

# Titre et description
st.title("📊 Forex & Or (XAU/USD) - Données Temps Réel")
st.markdown("""
Application de suivi des taux de change utilisant [FreeForexAPI.com](https://www.freeforexapi.com/)  
*Données avec actualisation automatique toutes les 30 secondes*
""")

# Liste des instruments disponibles
INSTRUMENTS = {
    "EUR/USD": "EURUSD",
    "USD/JPY": "USDJPY",
    "GBP/USD": "GBPUSD",
    "XAU/USD (Or)": "XAUUSD",
    "USD/CHF": "USDCHF",
    "AUD/USD": "AUDUSD"
}

# Fonction pour récupérer les données
def get_realtime_data(pair):
    try:
        response = requests.get(f"https://www.freeforexapi.com/api/live?pairs={pair}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data["code"] == 200:
                return {
                    "rate": data["rates"][pair]["rate"],
                    "timestamp": datetime.fromtimestamp(data["rates"][pair]["timestamp"])
                }
        return None
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return None

# Interface utilisateur
selected_pair = st.selectbox(
    "Sélectionnez un instrument:",
    options=list(INSTRUMENTS.keys()),
    index=0
)

pair_code = INSTRUMENTS[selected_pair]

# Conteneur pour les données
data_container = st.empty()
chart_container = st.empty()
history_container = st.empty()

# Initialisation des données historiques
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["timestamp", "rate"])

# Actualisation automatique
refresh_rate = 30  # secondes
last_update = st.empty()

while True:
    # Récupération des données
    data = get_realtime_data(pair_code)
    
    if data:
        # Mise à jour de l'historique
        new_row = pd.DataFrame([{
            "timestamp": data["timestamp"],
            "rate": data["rate"]
        }])
        st.session_state.history = pd.concat([st.session_state.history, new_row]).drop_duplicates()
        
        # Affichage des données
        with data_container.container():
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Prix actuel",
                    value=f"{data['rate']:.5f}",
                    help="Dernier taux de change"
                )
            with col2:
                st.metric(
                    label="Dernière actualisation",
                    value=data["timestamp"].strftime("%H:%M:%S"),
                    help="Heure de la dernière mise à jour"
                )
        
        # Graphique historique
        with chart_container.container():
            if len(st.session_state.history) > 1:
                st.line_chart(
                    st.session_state.history.set_index("timestamp"),
                    height=300
                )
        
        # Tableau historique
        with history_container.container():
            st.dataframe(
                st.session_state.history.sort_values("timestamp", ascending=False).head(10),
                hide_index=True,
                column_config={
                    "timestamp": "Heure",
                    "rate": "Taux"
                }
            )
    
    # Indicateur d'actualisation
    last_update.caption(f"Prochaine actualisation dans {refresh_rate} secondes...")
    
    # Pause avant rafraîchissement
    time.sleep(refresh_rate)
