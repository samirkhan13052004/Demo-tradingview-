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

# Injecting exactly your calculator.html CSS logic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    :root {
        --text-primary: #1c1c1e;
        --text-secondary: #6e6e73;
        --buy-color: #34c759; 
        --sell-color: #ff3b30; 
        --blue-color: #007aff; 
        --yellow-color: #FFCC00; 
        --calc-btn-color: #f04770; 
    }

    /* Base Body (iOS Light Theme from your HTML) */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
        background-color: #f2f2f7;
        background-image: 
            radial-gradient(circle at 15% 30%, rgba(0, 122, 255, 0.08), transparent 50%),
            radial-gradient(circle at 85% 20%, rgba(52, 199, 89, 0.08), transparent 50%),
            radial-gradient(circle at 50% 80%, rgba(255, 59, 48, 0.05), transparent 50%);
        background-attachment: fixed;
        color: #1c1c1e;
    }
    
    /* Hide Streamlit Defaults */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Titles */
    .algo-title { text-align: center; font-size: 34px; font-weight: 900; letter-spacing: -0.5px; margin-top: 10px; margin-bottom: 5px; color: #000; text-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .algo-subtitle { text-align: center; color: #6e6e73; margin-bottom: 30px; font-size: 15px; font-weight: 600;}
    
    /* Risk Selector (Like your Toggle Tabs) */
    div[data-testid="stRadio"] > div { display: flex; background: rgba(0, 0, 0, 0.06); padding: 5px; border-radius: 14px; gap: 5px; justify-content: center; }
    div[data-testid="stRadio"] > div > label {
        flex: 1; text-align: center; padding: 10px 5px; border-radius: 10px;
        font-size: 15px !important; font-weight: 700; color: #6e6e73; cursor: pointer;
        transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
        border: none; background: transparent;
    }
    /* Active State for Radio */
    div[data-testid="stRadio"] > div > label[data-baseweb="radio"]:has(input:checked) {
        background: #ffffff; color: #000; box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    div[data-testid="stRadio"] div[data-testid="stMarkdownContainer"] p { font-size: 15px !important; font-weight: 700; margin: 0; }
    
    /* Results Floating Card */
    .floating-card {
        background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 0;
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.08); overflow: hidden; margin-top: 20px;
        border: 1px solid rgba(255,255,255,1);
    }
    
    /* Custom Light Table */
    .light-table { width: 100%; border-collapse: collapse; }
    .light-table th { background: rgba(0, 0, 0, 0.04); color: #6e6e73; padding: 16px; text-align: center; font-weight: 800; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid rgba(0,0,0,0.05); }
    .light-table td { padding: 16px; color: #1c1c1e; text-align: center; border-bottom: 1px solid rgba(0,0,0,0.05); font-weight: 700; font-size: 15px; }
    .light-table tr:last-child td { border-bottom: none; }
    .light-table tr:hover { background: rgba(0, 122, 255, 0.04); }
    
    /* Text Colors from Calculator */
    .color-buy { color: #34c759; font-weight: 900; }
    .color-sell { color: #ff3b30; font-weight: 900; }
    .color-blue { color: #007aff; font-weight: 900; }
    .color-black { color: #000000; font-weight: 900; font-size: 16px; }
    
    /* Action Button (Like Calc Btn) */
    .tv-btn { 
        background: #007aff; color: white !important; padding: 10px 18px; border-radius: 12px; 
        text-decoration: none; font-weight: 800; font-size: 13px; display: inline-block;
        transition: 0.3s; box-shadow: 0 6px 15px rgba(0, 122, 255, 0.3); text-transform: uppercase;
    }
    .tv-btn:hover { transform: scale(0.96); box-shadow: 0 4px 10px rgba(0, 122, 255, 0.3); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIN UI (iOS Style)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['smartApi'] = None

if not st.session_state['authenticated']:
    st.markdown('<div class="algo-title">Shahrukh Scanner Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="algo-subtitle">Connect your Angel One API</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="floating-card" style="padding:30px;">', unsafe_allow_html=True)
        api_key = st.text_input("SmartAPI Key", type="password")
        client_code = st.text_input("Client Code")
        password = st.text_input("Angel One PIN", type="password")
        totp_secret = st.text_input("TOTP Secret", type="password")
        
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
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. PRO DASHBOARD & LIVE DATA LOGIC
# ==========================================
else:
    st.markdown('<div class="algo-title">Shahrukh Algo Scanner</div>', unsafe_allow_html=True)
    st.markdown('<div class="algo-subtitle">15-Min ORB • VWAP • 10 EMA • Live Angel One Data</div>', unsafe_allow_html=True)

    # 100% Matching Risk Tabs
    selected_risk = st.radio(
        "Risk Per Trade (₹):", 
        options=[250, 500, 750, 1000, 1500, 2000],
        index=3,
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    leverage = 5 
    
    # ------------------------------------------
    # 🔴 REAL DATA FETCHING LOGIC (For Live Market)
    # ------------------------------------------
    # नोट: लाइव मार्केट में यहाँ Angel One के getCandleData से 750 स्टॉक्स का लूप चलेगा। 
    # अभी आपको दिखाने के लिए मैंने 3 स्टॉक रखे हैं, जिनमें से RELIANCE की कंडीशन मैंने जानबूझकर ट्रू (True) की है 
    # ताकि आपको कम से कम 1 असली स्टॉक दिखे और डिज़ाइन चेक कर सकें।
    
    def fetch_live_stock_data():
        # असली API कॉल यहाँ आएगी: st.session_state['smartApi'].getCandleData(...)
        return [
            {"Symbol": "RELIANCE", "LTP": 2950.50, "Open": 2930.00, "15M_High": 2945.00, "15M_Low": 2925.00, "VWAP": 2940.00, "EMA_10": 2942.00, "ATR": 8.50, "RVOL": 1.6}, # 🟢 True Breakout
            {"Symbol": "TCS", "LTP": 4015.00, "Open": 4020.00, "15M_High": 4030.00, "15M_Low": 4005.00, "VWAP": 4010.00, "EMA_10": 4012.00, "ATR": 10.00, "RVOL": 0.8}, # 🔴 Failed
            {"Symbol": "ZOMATO", "LTP": 160.00, "Open": 158.00, "15M_High": 164.50, "15M_Low": 158.00, "VWAP": 162.00, "EMA_10": 163.50, "ATR": 2.50, "RVOL": 2.2}   # 🔴 Failed (No Breakout)
        ]

    raw_data_stream = fetch_live_stock_data()
    processed_signals = []
    current_time = datetime.now().strftime("%I:%M %p")

    # STRICT LOGIC FILTER
    for stock in raw_data_stream:
        ltp = stock["LTP"]
        orb_high = stock["15M_High"]
        
        # यह लाइन यह पक्का करती है कि जब तक स्टॉक ORB High नहीं तोड़ेगा, स्कैनर में नहीं दिखेगा!
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
    # 4. RENDER 100% CALCULATOR.HTML TABLE
    # ==========================================
    if processed_signals:
        table_html = """
        <div class="floating-card">
            <table class="light-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Stock</th>
                        <th>Signal</th>
                        <th>Entry (₹)</th>
                        <th>Stop Loss</th>
                        <th>Quantity</th>
                        <th>Margin (5x)</th>
                        <th>Target (1.5x)</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for sig in processed_signals:
            tv_link = f"https://in.tradingview.com/chart/?symbol=NSE:{sig['Stock']}&interval=5"
            table_html += f"""
                <tr>
                    <td style="color:#6e6e73; font-weight:600;">{sig['Time']}</td>
                    <td class="color-black">{sig['Stock']}</td>
                    <td class="color-buy">BUY</td>
                    <td class="color-blue">{sig['Entry']:.2f}</td>
                    <td class="color-sell">{sig['SL']:.2f}</td>
                    <td style="font-weight:900;">{sig['Qty']}</td>
                    <td style="color:#000;">₹{sig['Margin']:,}</td>
                    <td class="color-buy">{sig['Target']:.2f}</td>
                    <td><a href="{tv_link}" target="_blank" class="tv-btn">View Chart</a></td>
                </tr>
            """
        
        table_html += "</tbody></table></div>"
        
        # Display the custom iOS style Table
        st.markdown(table_html, unsafe_allow_html=True)
        
        # Add Calculate Button style from your HTML for quick refresh
        st.markdown(f"""
            <br>
            <button onclick="window.location.reload();" style="
                width: 100%; padding: 20px; background: #f04770; color: #fff; border: none; border-radius: 20px;
                font-size: 18px; font-weight: 800; letter-spacing: 1px; cursor: pointer; margin-top: 10px;
                box-shadow: 0 12px 25px rgba(240, 71, 112, 0.3); text-transform: uppercase; font-family: inherit;">
                Refresh Live Scanner
            </button>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div class="floating-card" style="text-align:center; padding: 50px 20px;">
            <h3 style="color:#1c1c1e; font-weight:900;">⏳ Waiting for Perfect Setup...</h3>
            <p style="color:#6e6e73; font-weight:600; font-size:15px;">अभी मार्केट में कोई भी स्टॉक आपके 15-Min ब्रेकआउट और इंडिकेटर रूल्स को मैच नहीं कर रहा है।</p>
        </div>
        """, unsafe_allow_html=True)
