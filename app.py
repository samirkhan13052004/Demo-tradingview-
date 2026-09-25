import streamlit as st
import pandas as pd
from datetime import datetime
import math
import pyotp
from SmartApi import SmartConnect

# ==========================================
# 1. PAGE CONFIGURATION & 100% CALCULATOR CSS
# ==========================================
st.set_page_config(page_title="Shahrukh Algo PRO", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

    /* Base Body (iOS Light Theme from your HTML) */
    .stApp {
        font-family: "Inter", -apple-system, sans-serif;
        background-color: #f2f2f7;
        background-image: 
            radial-gradient(circle at 15% 30%, rgba(0, 122, 255, 0.08), transparent 50%),
            radial-gradient(circle at 85% 20%, rgba(52, 199, 89, 0.08), transparent 50%);
        background-attachment: fixed;
        color: #1c1c1e;
    }
    
    /* Hide Streamlit Defaults */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Titles */
    .algo-title { text-align: center; font-size: 34px; font-weight: 900; letter-spacing: -0.5px; margin-top: 10px; margin-bottom: 5px; color: #1c1c1e; }
    .algo-subtitle { text-align: center; color: #6e6e73; margin-bottom: 30px; font-size: 15px; font-weight: 600;}
    
    /* =======================================
       FIX 1: INPUT BOXES & BUTTONS (Like Calculator)
       ======================================= */
    div[data-testid="stTextInput"] input {
        background-color: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        border-radius: 14px !important;
        padding: 14px 16px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #1c1c1e !important;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.02) !important;
    }
    
    div[data-testid="stButton"] button {
        background: #f04770 !important;
        color: #ffffff !important;
        border-radius: 16px !important;
        border: none !important;
        padding: 14px !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        box-shadow: 0 10px 20px rgba(240, 71, 112, 0.25) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div[data-testid="stButton"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 25px rgba(240, 71, 112, 0.35) !important;
    }

    /* =======================================
       FIX 2: RISK SELECTOR (Toggle Tabs)
       ======================================= */
    div[data-testid="stRadio"] {
        background: #e3e3e8;
        padding: 4px;
        border-radius: 14px;
    }
    div[data-testid="stRadio"] > div {
        gap: 0px;
    }
    div[data-testid="stRadio"] label {
        padding: 10px 0px;
        border-radius: 12px;
        text-align: center;
        justify-content: center;
    }
    /* Hide original radio circle */
    div[data-testid="stRadio"] label span[data-baseweb="radio"] {
        display: none !important;
    }
    div[data-testid="stRadio"] label p {
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    /* =======================================
       FIX 3: RESULTS TABLE (Glassmorphism)
       ======================================= */
    .floating-card {
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.06);
        overflow: hidden;
        border: 1px solid rgba(255,255,255,1);
        margin-top: 10px;
    }
    .light-table { width: 100%; border-collapse: collapse; background: #ffffff; }
    .light-table th { background: rgba(0,0,0,0.03); color: #8e8e93; padding: 16px; text-align: center; font-weight: 800; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #f2f2f7; }
    .light-table td { padding: 18px 16px; color: #1c1c1e; text-align: center; border-bottom: 1px solid #f2f2f7; font-weight: 700; font-size: 15px; }
    .light-table tr:hover { background: #f9f9fb; }
    
    .color-buy { color: #34c759; font-weight: 900; }
    .color-sell { color: #ff3b30; font-weight: 900; }
    .color-blue { color: #007aff; font-weight: 900; }
    
    .tv-btn { 
        background: #007aff; color: white !important; padding: 8px 16px; border-radius: 10px; 
        text-decoration: none; font-weight: 800; font-size: 13px; display: inline-block;
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.25);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIN UI (100% MATCHING CALCULATOR INPUTS)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['smartApi'] = None

if not st.session_state['authenticated']:
    st.markdown('<div class="algo-title">Scanner Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="algo-subtitle">Connect your Angel One API</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        api_key = st.text_input("SmartAPI Key", placeholder="Enter API Key", type="password")
        client_code = st.text_input("Client Code", placeholder="e.g. S123456")
        password = st.text_input("Angel One PIN", placeholder="4 Digit PIN", type="password")
        totp_secret = st.text_input("TOTP Secret", placeholder="Enter TOTP Secret", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("CONNECT & START", use_container_width=True):
            if api_key and client_code and password and totp_secret:
                try:
                    totp = pyotp.TOTP(totp_secret).now()
                    smartApi = SmartConnect(api_key=api_key)
                    auth = smartApi.generateSession(client_code, password, totp)
                    if auth.get('status'):
                        st.session_state['authenticated'] = True
                        st.session_state['smartApi'] = smartApi
                        st.rerun()
                    else:
                        st.error("❌ Invalid Credentials")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ==========================================
# 3. PRO DASHBOARD & LIVE DATA
# ==========================================
else:
    st.markdown('<div class="algo-title">Shahrukh Algo Scanner</div>', unsafe_allow_html=True)
    st.markdown('<div class="algo-subtitle">15-Min ORB • VWAP • 10 EMA • Live Angel One Data</div>', unsafe_allow_html=True)

    selected_risk = st.radio(
        "Select Risk Per Trade (₹):", 
        options=[250, 500, 750, 1000, 1500, 2000],
        index=3,
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    leverage = 5 
    
    # 🔴 डमी डेटा (चेक करने के लिए कि स्टॉक सही से दिखे)
    def fetch_live_stock_data():
        return [
            {"Symbol": "RELIANCE", "LTP": 2950.50, "Open": 2930.00, "15M_High": 2940.00, "15M_Low": 2925.00, "VWAP": 2945.00, "EMA_10": 2942.00, "ATR": 8.50, "RVOL": 1.6},
        ]

    raw_data_stream = fetch_live_stock_data()
    processed_signals = []
    current_time = datetime.now().strftime("%I:%M %p")

    for stock in raw_data_stream:
        ltp = stock["LTP"]
        orb_high = stock["15M_High"]
        
        # Conditions
        cond_breakout = ltp > orb_high                    
        cond_green = ltp > stock["Open"]                  
        cond_indicators = (ltp > stock["VWAP"]) and (ltp > stock["EMA_10"]) 
        cond_rvol = stock["RVOL"] >= 1.5                  
        
        if (50 <= ltp <= 3500) and cond_breakout and cond_green and cond_indicators and cond_rvol:
            sl_price = round(ltp - stock["ATR"], 2) 
            risk_points = round(abs(ltp - sl_price), 2)
            
            if risk_points > 0:
                qty = math.floor(selected_risk / risk_points) 
                
                if qty > 0:
                    capital_req = math.ceil((qty * ltp) / leverage) 
                    target_price = round(ltp + (risk_points * 1.5), 2) 
                    
                    processed_signals.append({
                        "Time": current_time,
                        "Stock": stock["Symbol"],
                        "Entry": ltp,
                        "SL": sl_price,
                        "Qty": qty,
                        "Margin": capital_req,
                        "Target": target_price
                    })

    # ==========================================
    # 4. BUG FIXED: NO INDENTATION HTML RENDER
    # ==========================================
    if processed_signals:
        # मैंने यहाँ HTML को एक ही लाइन में जोड़ दिया है ताकि Streamlit इसे कोड ब्लॉक न समझे।
        html = "<div class='floating-card'><table class='light-table'>"
        html += "<thead><tr><th>Time</th><th>Stock</th><th>Signal</th><th>Entry (₹)</th><th>Stop Loss</th><th>Quantity</th><th>Margin (5x)</th><th>Target</th><th>Action</th></tr></thead><tbody>"
        
        for sig in processed_signals:
            tv_link = f"https://in.tradingview.com/chart/?symbol=NSE:{sig['Stock']}&interval=5"
            html += f"<tr><td style='color:#8e8e93;'>{sig['Time']}</td><td style='font-weight:900;'>{sig['Stock']}</td><td class='color-buy'>BUY</td><td class='color-blue'>{sig['Entry']:.2f}</td><td class='color-sell'>{sig['SL']:.2f}</td><td style='font-weight:900;'>{sig['Qty']}</td><td style='color:#1c1c1e;'>₹{sig['Margin']:,}</td><td class='color-buy'>{sig['Target']:.2f}</td><td><a href='{tv_link}' target='_blank' class='tv-btn'>CHART</a></td></tr>"
        
        html += "</tbody></table></div>"
        
        st.markdown(html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("REFRESH LIVE SCANNER", use_container_width=True):
            st.rerun()
        
    else:
        st.markdown("<div class='floating-card' style='text-align:center; padding: 40px;'><h3 style='color:#1c1c1e;'>⏳ Waiting for Setup...</h3></div>", unsafe_allow_html=True)
