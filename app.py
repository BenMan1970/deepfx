import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Configuration de l'application
st.set_page_config(
    page_title="Forex & Or en Temps Réel - Version Stable",
    page_icon="💹",
    layout="wide"
)

# Titre et description
st.title("📊 Forex & Or (XAU/USD) - Données Temps Réel")
st.markdown("""
Application de suivi des taux de change utilisant [FreeForexAPI.com](https://www.freeforexapi.com/)  
*Données avec actualisation automatique toutes les 30 secondes*
""")

# Liste des instruments avec vérification de disponibilité
INSTRUMENTS = {
    "EUR/USD": "EURUSD",
    "USD/JPY": "USDJPY", 
    "GBP/USD": "GBPUSD",
    "XAU/USD (Or)": "XAUUSD",
    "USD/CHF": "USDCHF",
    "AUD/USD": "AUDUSD"
}

# Fonction améliorée avec gestion d'erreur robuste
def get_realtime_data(pair):
    try:
        response = requests.get(
            f"https://www.freeforexapi.com/api/live?pairs={pair}",
            timeout=10
        )
        
        # Vérification complète de la réponse
        if response.status_code != 200:
            raise ConnectionError(f"Code HTTP {response.status_code}")
            
        data = response.json()
        
        if not data.get("rates"):
            raise ValueError("Données indisponibles pour cette paire")
            
        if pair not in data["rates"]:
            raise KeyError(f"Paire {pair} non trouvée dans la réponse")
            
        return {
            "rate": data["rates"][pair]["rate"],
            "timestamp": datetime.fromtimestamp(data["rates"][pair]["timestamp"])
        }
        
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {str(e)}")
        return None

# Interface utilisateur
selected_pair = st.selectbox(
    "Sélectionnez un instrument:",
    options=list(INSTRUMENTS.keys()),
    index=0
)

pair_code = INSTRUMENTS[selected_pair]

# Conteneurs
data_container = st.empty()
status_container = st.empty()
chart_container = st.empty()

# Initialisation historique
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["timestamp", "rate"])

# Boucle principale améliorée
refresh_rate = 30  # secondes

while True:
    current_time = datetime.now().strftime("%H:%M:%S")
    
    try:
        data = get_realtime_data(pair_code)
        
        if data:
            # Mise à jour historique
            new_row = pd.DataFrame([{
                "timestamp": data["timestamp"],
                "rate": data["rate"]
            }])
            
            st.session_state.history = pd.concat(
                [st.session_state.history, new_row]
            ).drop_duplicates().tail(100)  # Limite à 100 points
            
            # Affichage
            with data_container.container():
                cols = st.columns(3)
                cols[0].metric("Instrument", selected_pair)
                cols[1].metric("Prix actuel", f"{data['rate']:.5f}")
                cols[2].metric("Dernière mise à jour", current_time)
                
            with chart_container.container():
                if len(st.session_state.history) > 1:
                    st.line_chart(
                        st.session_state.history.set_index("timestamp"),
                        height=300,
                        use_container_width=True
                    )
        
        status_container.success(f"Données actualisées à {current_time} | Prochaine actualisation dans {refresh_rate}s")
        
    except Exception as e:
        status_container.error(f"Erreur à {current_time}: {str(e)}")
    
    time.sleep(refresh_rate)
   
