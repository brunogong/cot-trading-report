import os
import requests
import schedule
import time
from datetime import datetime
from telegram import Bot
import asyncio

# ========================================
# CONFIGURAZIONE da variabili ambiente
# ========================================

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# ========================================
# FUNZIONI
# ========================================

def get_cot_data():
    """Scarica dati COT"""
    try:
        url = "https://publicreporting.cftc.gov/resource/jun7-fc8e.json"
        params = {
            "$limit": 50,
            "$order": "report_date_as_yyyy_mm_dd DESC"
        }
        response = requests.get(url, params=params, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Errore: {e}")
        return None

def analyze_cot(data):
    """Analizza e genera report"""
    
    instruments = {
        'EURO FX': '💶 EUR/USD',
        'BRITISH POUND': '💷 GBP/USD',
        'JAPANESE YEN': '💴 USD/JPY',
        'AUSTRALIAN DOLLAR': '🦘 AUD/USD',
        'GOLD': '🥇 GOLD',
        'CRUDE OIL': '🛢️ OIL'
    }
    
    report = "━━━━━━━━━━━━━━━━━━━━\n"
    report += f"📊 COT REPORT\n"
    report += f"{datetime.now().strftime('%d %B %Y')}\n"
    report += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for cftc_name, display_name in instruments.items():
        instrument_data = next(
            (item for item in data if cftc_name.lower() in item.get('market_and_exchange_names', '').lower()),
            None
        )
        
        if instrument_data:
            try:
                comm_long = float(instrument_data.get('dealer_positions_long_all', 0))
                comm_short = float(instrument_data.get('dealer_positions_short_all', 0))
                net = comm_long - comm_short
                
                if net > 20000:
                    bias = "COMPRA 🟢🟢"
                elif net > 5000:
                    bias = "COMPRA 🟢"
                elif net < -20000:
                    bias = "VENDI 🔴🔴"
                elif net < -5000:
                    bias = "VENDI 🔴"
                else:
                    bias = "NEUTRALE ⚪"
                
                report += f"{display_name}\n"
                report += f"NET: {net:,.0f}\n"
                report += f"Bias: {bias}\n\n"
                
            except:
                report += f"{display_name}: Dati N/A\n\n"
    
    report += "━━━━━━━━━━━━━━━━━━━━\n"
    return report

async def send_telegram(text):
    """Invia su Telegram"""
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=text)
        print(f"✅ Inviato: {datetime.now()}")
    except Exception as e:
        print(f"❌ Errore: {e}")

def send_report():
    """Funzione principale"""
    print(f"🔄 Generazione report: {datetime.now()}")
    data = get_cot_data()
    if data:
        report = analyze_cot(data)
        asyncio.run(send_telegram(report))

# ========================================
# SCHEDULER
# ========================================

# Ogni venerdì alle 22:30
schedule.every().friday.at("22:30").do(send_report)

# ========================================
# MAIN
# ========================================

if __name__ == "__main__":
    print("🤖 Bot avviato!")
    
    # Test immediato
    send_report()
    
    # Loop
    while True:
        schedule.run_pending()
        time.sleep(60)
