import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="COT Trading Report",
    page_icon="📊",
    layout="wide"
)

st.title("📊 COT Trading Report")
st.caption(f"Ultimo aggiornamento: {datetime.now().strftime('%d %B %Y, %H:%M')}")

# ========================================
# FUNZIONE SCARICA DATI COT
# ========================================

@st.cache_data(ttl=3600)  # Cache 1 ora
def get_cot_data():
    try:
        url = "https://publicreporting.cftc.gov/resource/jun7-fc8e.json"
        params = {
            "$limit": 100,
            "$order": "report_date_as_yyyy_mm_dd DESC"
        }
        response = requests.get(url, params=params, timeout=30)
        return response.json()
    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")
        return None

# ========================================
# ANALISI COT
# ========================================

def analyze_instrument(data, instrument_name):
    """Analizza singolo strumento"""
    
    instrument_data = next(
        (item for item in data if instrument_name.lower() in item.get('market_and_exchange_names', '').lower()),
        None
    )
    
    if not instrument_data:
        return None
    
    try:
        comm_long = float(instrument_data.get('dealer_positions_long_all', 0))
        comm_short = float(instrument_data.get('dealer_positions_short_all', 0))
        net_position = comm_long - comm_short
        
        # Determina bias e forza
        if net_position > 50000:
            bias = "COMPRA"
            strength = "🟢🟢🟢"
            color = "green"
        elif net_position > 20000:
            bias = "COMPRA"
            strength = "🟢🟢"
            color = "green"
        elif net_position > 5000:
            bias = "COMPRA"
            strength = "🟢"
            color = "lightgreen"
        elif net_position < -50000:
            bias = "VENDI"
            strength = "🔴🔴🔴"
            color = "red"
        elif net_position < -20000:
            bias = "VENDI"
            strength = "🔴🔴"
            color = "red"
        elif net_position < -5000:
            bias = "VENDI"
            strength = "🔴"
            color = "lightcoral"
        else:
            bias = "NEUTRALE"
            strength = "⚪"
            color = "gray"
        
        return {
            'net': net_position,
            'bias': bias,
            'strength': strength,
            'color': color,
            'long': comm_long,
            'short': comm_short
        }
    except:
        return None

# ========================================
# INTERFACCIA
# ========================================

# Scarica dati
with st.spinner('📥 Caricamento dati COT...'):
    data = get_cot_data()

if data:
    
    st.success("✅ Dati caricati con successo")
    
    # Data del report
    if data and len(data) > 0:
        report_date = data[0].get('report_date_as_yyyy_mm_dd', 'N/A')
        st.info(f"📅 Report COT del: **{report_date}**")
    
    st.markdown("---")
    
    # Strumenti da analizzare
    instruments = {
        '💶 EUR/USD': 'EURO FX',
        '💷 GBP/USD': 'BRITISH POUND',
        '💴 USD/JPY': 'JAPANESE YEN',
        '🦘 AUD/USD': 'AUSTRALIAN DOLLAR',
        '🥇 GOLD': 'GOLD',
        '🛢️ OIL': 'CRUDE OIL'
    }
    
    # Layout a 2 colonne
    col1, col2 = st.columns(2)
    
    for idx, (display_name, cftc_name) in enumerate(instruments.items()):
        
        result = analyze_instrument(data, cftc_name)
        
        # Alterna colonne
        col = col1 if idx % 2 == 0 else col2
        
        with col:
            with st.container():
                st.markdown(f"### {display_name}")
                
                if result:
                    # Card con info
                    st.markdown(
                        f"""
                        <div style='padding: 20px; background-color: {result['color']}22; border-radius: 10px; border-left: 5px solid {result['color']}'>
                            <h2 style='color: {result['color']}; margin: 0;'>{result['bias']} {result['strength']}</h2>
                            <p style='margin: 10px 0 0 0; font-size: 18px;'>
                                Commercial NET: <strong>{result['net']:,.0f}</strong>
                            </p>
                            <p style='margin: 5px 0; font-size: 14px; color: gray;'>
                                Long: {result['long']:,.0f} | Short: {result['short']:,.0f}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("Dati non disponibili")
                
                st.markdown("")  # Spacing
    
    # ========================================
    # RIEPILOGO
    # ========================================
    
    st.markdown("---")
    st.markdown("## 📌 Riepilogo Settimanale")
    
    # Crea tabella riepilogo
    summary_data = []
    for display_name, cftc_name in instruments.items():
        result = analyze_instrument(data, cftc_name)
        if result:
            summary_data.append({
                'Strumento': display_name,
                'Bias': f"{result['bias']} {result['strength']}",
                'Commercial NET': f"{result['net']:,.0f}"
            })
    
    if summary_data:
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # ========================================
    # NOTE
    # ========================================
    
    st.markdown("---")
    st.markdown("### 💡 Come Usare Questo Report")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🟢 COMPRA**
        - Cerca setup LONG
        - Supporti chiave
        - Pattern rialzisti
        """)
    
    with col2:
        st.markdown("""
        **🔴 VENDI**
        - Cerca setup SHORT
        - Resistenze chiave
        - Pattern ribassisti
        """)
    
    with col3:
        st.markdown("""
        **⚪ NEUTRALE**
        - Evita trade
        - Aspetta chiarezza
        - Focus su altri asset
        """)
    
    st.markdown("---")
    st.caption("⚠️ I dati COT hanno 3 giorni di ritardo. Usa come bias direzionale, non segnale di entry immediato.")
    
    # Pulsante refresh
    if st.button("🔄 Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

else:
    st.error("❌ Impossibile caricare i dati COT. Riprova più tardi.")

# Footer
st.markdown("---")
st.caption("📊 COT Data Source: CFTC | Aggiornato ogni venerdì")
