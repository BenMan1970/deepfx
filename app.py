import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Configuration éprouvée
st.set_page_config(
    page_title="Forex Tracker PRO",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Style CSS professionnel
st.markdown("""
<style>
    .header-style {
        font-size: 26px;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 30px;
    }
    .data-card {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .error-message {
        color: #d32f2f;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header amélioré
st.markdown('<p class="header-style">📊 Forex & Or (XAU/USD) - Monitor PRO</p>', unsafe_allow_html=True)
st.caption("Données temps réel via FreeForexAPI | Actualisation automatique")

# Paires disponibles avec fallback
FOREX_PAIRS = {
    "EUR/USD": {"code": "EURUSD", "fallback": 1.07},
    "USD/JPY": {"code": "USDJPY", "fallback": 151.50},
    "GBP/USD": {"code": "GBPUSD", "fallback": 1.25},
    "XAU/USD": {"code": "XAUUSD", "fallback": 1950.00},
    "USD/CHF": {"code": "USDCHF", "fallback": 0.91},
    "AUD/USD": {"code": "AUDUSD", "fallback": 0.66}
}

# Fonction robuste avec fallback
@st.cache_data(ttl=30, show_spinner=False)
def get_forex_data(pair_code):
    try:
        response = requests.get(
            f"https://www.freeforexapi.com/api/live?pairs={pair_code}",
            timeout=10,
            headers={'Cache-Control': 'no-cache'}
        )
        
        # Double vérification des données
        if response.status_code == 200:
            data = response.json()
            if data and "rates" in data and pair_code in data["rates"]:
                return {
                    "success": True,
                    "rate": data["rates"][pair_code]["rate"],
                    "timestamp": datetime.fromtimestamp(data["rates"][pair_code]["timestamp"])
                }
        
        return {"success": False, "rate": None}
        
    except Exception:
        return {"success": False, "rate": None}

# Initialisation session state
if "df_history" not in st.session_state:
    st.session_state.df_history = pd.DataFrame(columns=["pair", "rate", "timestamp"])

# Sidebar professionnelle
with st.sidebar:
    st.header("Configuration")
    selected_pair = st.selectbox(
        "Paire Forex:",
        options=list(FOREX_PAIRS.keys()),
        index=0
    )
    auto_refresh = st.checkbox("Actualisation auto (30s)", True)
    st.markdown("---")
    st.caption("Dernière mise à jour:")
    last_update = st.empty()

# Conteneurs principaux
main_container = st.container()
error_container = st.empty()
chart_container = st.container()

# Boucle principale optimisée
def main_loop():
    pair_info = FOREX_PAIRS[selected_pair]
    pair_code = pair_info["code"]
    
    # Récupération données
    data = get_forex_data(pair_code)
    
    with main_container:
        # Carte de données
        with st.container(border=True):
            cols = st.columns(2)
            cols[0].subheader(f"**{selected_pair}**")
            
            if data["success"]:
                rate = data["rate"]
                cols[1].subheader(f"`{rate:.5f}`")
                last_update.text(datetime.now().strftime("%H:%M:%S"))
                
                # Mise à jour historique
                new_row = pd.DataFrame([{
                    "pair": selected_pair,
                    "rate": rate,
                    "timestamp": data["timestamp"]
                }])
                
                st.session_state.df_history = pd.concat(
                    [st.session_state.df_history, new_row]
                ).drop_duplicates().tail(100)
                
            else:
                cols[1].subheader(f"`{pair_info['fallback']:.5f}` (fallback)")
                error_container.error("⚠️ Données temporairement indisponibles - Mode fallback activé")
    
    # Graphique
    with chart_container:
        if not st.session_state.df_history.empty:
            chart_data = st.session_state.df_history[
                st.session_state.df_history["pair"] == selected_pair
            ].set_index("timestamp")
            
            st.line_chart(
                chart_data["rate"],
                height=350,
                use_container_width=True
            )

# Gestion de l'actualisation
if auto_refresh:
    while True:
        main_loop()
        time.sleep(30)
else:
    main_loop()
  
