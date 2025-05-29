import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Configuration robuste
st.set_page_config(
    page_title="Forex Tracker (Version Stable)",
    page_icon="💹",
    layout="wide"
)

# Titre avec style
st.markdown("""
<h1 style='text-align: center; color: #1E90FF;'>
📊 Forex & Or (XAU/USD) - Données Temps Réel
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin-bottom: 20px;'>
Application utilisant <a href="https://www.freeforexapi.com">FreeForexAPI.com</a><br>
<small>Actualisation automatique toutes les 30 secondes</small>
</div>
""", unsafe_allow_html=True)

# Instruments disponibles avec vérification
AVAILABLE_PAIRS = {
    "EUR/USD": "EURUSD",
    "USD/JPY": "USDJPY",
    "GBP/USD": "GBPUSD",
    "XAU/USD (Or)": "XAUUSD",
    "USD/CHF": "USDCHF",
    "AUD/USD": "AUDUSD"
}

# Fonction sécurisée
def fetch_forex_data(pair_code):
    try:
        url = f"https://www.freeforexapi.com/api/live?pairs={pair_code}"
        response = requests.get(url, timeout=15)
        
        # Vérification en 3 étapes
        if response.status_code != 200:
            raise ConnectionError(f"Erreur HTTP {response.status_code}")
        
        data = response.json()
        
        if not isinstance(data, dict) or "rates" not in data:
            raise ValueError("Structure de données invalide")
            
        if pair_code not in data["rates"]:
            raise KeyError(f"Paire {pair_code} non disponible")
            
        return {
            "rate": round(data["rates"][pair_code]["rate"], 5),
            "time": datetime.fromtimestamp(data["rates"][pair_code]["timestamp"])
        }
        
    except Exception as e:
        st.session_state.last_error = str(e)
        return None

# Interface
selected = st.selectbox(
    "Sélectionnez une paire:",
    options=list(AVAILABLE_PAIRS.keys()),
    index=0
)

pair_code = AVAILABLE_PAIRS[selected]

# Initialisation
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["time", "rate"])
    st.session_state.last_error = None

# Conteneurs
status_bar = st.empty()
data_display = st.empty()
chart = st.empty()

# Boucle principale
while True:
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Récupération des données
    data = fetch_forex_data(pair_code)
    
    if data:
        # Mise à jour de l'historique
        new_entry = pd.DataFrame([{
            "time": data["time"],
            "rate": data["rate"]
        }])
        
        st.session_state.history = pd.concat(
            [st.session_state.history, new_entry]
        ).drop_duplicates().tail(50)  # Garde seulement les 50 dernières entrées
        
        # Affichage
        with data_display.container():
            cols = st.columns(3)
            cols[0].metric("Paire", selected)
            cols[1].metric("Taux actuel", f"{data['rate']:.5f}")
            cols[2].metric("Heure", data["time"].strftime("%H:%M:%S"))
            
        with chart.container():
            if len(st.session_state.history) > 1:
                st.line_chart(
                    st.session_state.history.set_index("time"),
                    height=350
                )
        
        status_bar.success(f"✅ Données actualisées à {current_time}")
        st.session_state.last_error = None
    else:
        error_msg = st.session_state.last_error or "Erreur inconnue"
        status_bar.error(f"❌ Dernière erreur ({current_time}): {error_msg}")
    
    time.sleep(30)  # 30 secondes entre les requêtes
  
