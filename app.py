import streamlit as st
import pandas as pd
from datetime import datetime
import math
import pyotp
from streamlit_autorefresh import st_autorefresh
from SmartApi import SmartConnect

# ==========================================
# 1. PAGE CONFIGURATION & PREMIUM CSS
# ==========================================
st.set_page_config(page_title="Shahrukh Algo PRO", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# 🌟 Advanced Premium UI - CSS Injection
st.markdown("""
    <style>
    /* Dark Theme Background */
    .stApp { background-color: #0b0e14; color: #d1d4dc; }
    
    /* Hide Streamlit Defaults */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Title Styling */
    .algo-title { font-size: 38px; font-weight: 800; color: #ffffff; text-align: center; margin-bottom: 5px; 
                  text-shadow: 0px 0px 20px rgba(41, 98, 255, 0.5); }
    .algo-subtitle { text-align: center; color: #787b86; margin-bottom: 30px; font-size: 16px; }
    
    /* Modern Risk Selector Buttons (Radio to Tabs) */
    div[data-testid="stRadio"] > div { display: flex; gap: 15px; justify-content: center; background: transparent; }
    div[data-testid="stRadio"] > div > label {
        background: rgba(30, 34, 45, 0.8); border: 1px solid #2a2e39; border-radius: 10px; padding: 12px 30px;
        color: #d1d4dc; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); font-weight: 600; font-size: 16px;
    }
    div[data-testid="stRadio"] > div > label:hover { border-color: #2962ff; color: white; transform: translateY(-2px); }
    div[data-testid="stRadio"] div[data-testid="stMarkdownContainer"] p { font-size: 18px !important; margin: 0; }
    
    /* Glassmorphism Data Table */
    .glass-table-container { overflow-x: auto; margin-top: 20px; border-radius: 15px; }
    .glass-table {
        width: 100%; border-collapse: collapse; background: rgba(30, 34, 45, 0.6);
        backdrop-filter: blur(12px); border-radius: 12px; overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4); border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .glass-table th { background: linear-gradient(90deg, #1e3a8a, #2962ff); color: white; padding: 16px; text-align: center; font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }
    .glass-table td { padding: 15px; color: #e2e8f0; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-weight: 500; font-size: 15px; }
    .glass-table tr:hover { background: rgba(41, 98, 255, 0.15); }
    
    /* Highlight Classes */
    .signal-buy { color: #00e676; font-weight: 800; text-shadow: 0 0 10px rgba(0, 230, 118, 0.4); font-size: 16px; }
    .tv-btn { background: #2962ff; color: white !important; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; transition: 0.3s; box-shadow: 0 4px 15px rgba(41,98,255,0.4); }
    .tv-btn:hover { background: #0039cb; box-shadow: 0 6px 20px rgba(41,98,255,0.6); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION & LOGIN
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown('<div class="algo-title">🔐 Shahrukh Algo Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="algo-subtitle">Angel One API Connection</div>', unsafe_allow_html=True)
    
    with st.container():
        api_key = st.text_input("SmartAPI Key", type="password")
        client_code = st.text_input("Client Code")
        password = st.text_input("PIN", type="password")
        totp_secret = st.text_input("Long TOTP Secret", type="password")

        if st.button("🚀 CONNECT & START LIVE SCANNER", use_container_width=True):
            if api_key and client_code and password and totp_secret:
                try:
                    totp = pyotp.TOTP(totp_secret).now()
                    smartApi = SmartConnect(api_key=api_key)
                    auth = smartApi.generateSession(client_code, password, totp)
                    if auth.get('status'):
                        st.session_state['authenticated'] = True
                        st.rerun()
                    else:
                        st.error("❌ Invalid Credentials")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ==========================================
# 3. PRO DASHBOARD
# ==========================================
else:
    st_autorefresh(interval=5 * 60 * 1000, key="data_refresh") # 5 Min Refresh

    st.markdown('<div class="algo-title">⚡ SHAHRUKH ALGO SCANNER</div>', unsafe_allow_html=True)
    st.markdown('<div class="algo-subtitle">15-Min ORB • VWAP • 10 EMA • 5x Leverage • Live Tracking</div>', unsafe_allow_html=True)

    # --- MODERN BUTTON RISK SELECTOR ---
    selected_risk = st.radio(
        "💰 Select Risk Per Trade (₹):", 
        options=[250, 500, 750, 1000, 1500, 2000],
        index=3,
        horizontal=True,
        label_visibility="hidden"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    leverage = 5 
    
    # ==========================================
    # 4. STRICT PINE SCRIPT LOGIC FILTER
    # ==========================================
    # नोट: यहाँ अभी रियल एंजेल वन डेटा लिंक करना बाकी है। 
    # आपके टेस्टिंग के लिए मैंने इसे 100% स्ट्रिक्ट रूल्स के साथ रखा है ताकि कोई गलत सिग्नल पास न हो।
    raw_data_stream = [
        {"Symbol": "RELIANCE", "LTP": 2950.50, "Open": 2930.00, "15M_High": 2945.00, "15M_Low": 2925.00, "VWAP": 2940.00, "EMA_10": 2942.00, "ATR": 8.50, "RVOL": 1.6},
        {"Symbol": "TCS", "LTP": 4015.00, "Open": 4020.00, "15M_High": 4030.00, "15M_Low": 4005.00, "VWAP": 4010.00, "EMA_10": 4012.00, "ATR": 10.00, "RVOL": 0.8}, # Fail: Red Candle & Not Breakout
        {"Symbol": "ZOMATO", "LTP": 165.20, "Open": 160.00, "15M_High": 164.50, "15M_Low": 158.00, "VWAP": 162.00, "EMA_10": 163.50, "ATR": 2.50, "RVOL": 2.2}
    ]

    processed_signals = []
    current_time = datetime.now().strftime("%H:%M:%S")

    for stock in raw_data_stream:
        ltp = stock["LTP"]
        orb_high = stock["15M_High"]
        
        # 🛡️ STRICT CONDITIONS (Pine Script Match)
        cond_breakout = ltp > orb_high                    # 15-Min ORB Breakout
        cond_green = ltp > stock["Open"]                  # Green Candle
        cond_indicators = (ltp > stock["VWAP"]) and (ltp > stock["EMA_10"]) # Above VWAP & EMA
        cond_rvol = stock["RVOL"] >= 1.5                  # Volume Filter
        
        # अगर स्टॉक ने ऊपर की सारी शर्तें पूरी कीं, तभी वह स्कैनर में आएगा!
        if (50 <= ltp <= 3500) and cond_breakout and cond_green and cond_indicators and cond_rvol:
            
            # --- CALCULATOR LOGIC ---
            sl_price = round(ltp - stock["ATR"], 2) # Stoploss using ATR
            risk_points = round(abs(ltp - sl_price), 2)
            
            if risk_points > 0:
                qty = math.floor(selected_risk / risk_points) # Qty = Risk / Points
                
                if qty > 0:
                    capital_req = math.ceil((qty * ltp) / leverage) # Margin Calculation
                    target_price = round(ltp + (risk_points * 1.5), 2) # 1:1.5 RR Target
                    
                    processed_signals.append({
                        "Time": current_time,
                        "Stock": stock["Symbol"],
                        "Entry": ltp,
                        "SL": sl_price,
                        "Risk_Pts": risk_points,
                        "Qty": qty,
                        "Margin": capital_req,
                        "Target": target_price
                    })

    # ==========================================
    # 5. RENDER PREMIUM HTML TABLE
    # ==========================================
    if processed_signals:
        table_html = """
        <div class="glass-table-container">
            <table class="glass-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Stock</th>
                        <th>Signal</th>
                        <th>Entry (₹)</th>
                        <th>Stop Loss (₹)</th>
                        <th>Qty</th>
                        <th>Required Margin (5x)</th>
                        <th>Target (1.5x)</th>
                        <th>Live Chart</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for sig in processed_signals:
            tv_link = f"https://in.tradingview.com/chart/?symbol=NSE:{sig['Stock']}&interval=5"
            table_html += f"""
                <tr>
                    <td>{sig['Time']}</td>
                    <td style="font-weight:bold; color:white;">{sig['Stock']}</td>
                    <td class="signal-buy">🟢 BUY</td>
                    <td>{sig['Entry']:.2f}</td>
                    <td style="color: #ff5252;">{sig['SL']:.2f}</td>
                    <td style="color: #ffd600;">{sig['Qty']}</td>
                    <td style="color: #00e676;">₹ {sig['Margin']:,}</td>
                    <td style="color: #ff9800;">{sig['Target']:.2f}</td>
                    <td><a href="{tv_link}" target="_blank" class="tv-btn">Open Chart 📈</a></td>
                </tr>
            """
        
        table_html += "</tbody></table></div>"
        
        # Display the custom HTML Table
        st.markdown(table_html, unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div style="text-align:center; padding: 40px; background: rgba(30, 34, 45, 0.4); border-radius: 12px; border: 1px dashed #3a3f50; margin-top: 20px;">
            <h3 style="color:#787b86;">⏳ Waiting for Perfect Setup...</h3>
            <p style="color:#787b86;">अभी मार्केट में कोई भी स्टॉक आपके 15-Min ब्रेकआउट और इंडिकेटर रूल्स को मैच नहीं कर रहा है। 5 मिनट में अपने आप रिफ्रेश होगा।</p>
        </div>
        """, unsafe_allow_html=True)
