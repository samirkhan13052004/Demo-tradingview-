import streamlit as st
import pandas as pd
from datetime import datetime
import math
import pyotp
from streamlit_autorefresh import st_autorefresh
from SmartApi import SmartConnect

# ==========================================
# 1. PAGE CONFIGURATION & ADVANCED UI (CSS)
# ==========================================
st.set_page_config(page_title="Shahrukh Algo Live", page_icon="⚡", layout="wide")

# Custom CSS for Modern "Button-Like" UI and Glassmorphism
st.markdown("""
    <style>
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    /* Make Radio Buttons look like Modern Action Buttons */
    div.stRadio > div {
        display: flex;
        flex-direction: row;
        gap: 15px;
        background-color: transparent;
    }
    div.stRadio > div > label {
        background: #1E222D;
        padding: 10px 25px;
        border-radius: 8px;
        border: 1px solid #2962ff;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    div.stRadio > div > label:hover {
        background: #2962ff;
        border-color: #ffffff;
    }
    
    /* Table Styling to match TradingView PineScript feel */
    thead tr th {
        background-color: #2962ff !important;
        color: white !important;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# ==========================================
# 3. LOGIN SCREEN
# ==========================================
if not st.session_state['authenticated']:
    st.title("🔐 Shahrukh Algo Login")
    with st.form("login_form"):
        col1, col2 = st.columns(2)
        with col1:
            api_key = st.text_input("SmartAPI Key", type="password")
            client_code = st.text_input("Client Code (e.g. A123456)")
        with col2:
            password = st.text_input("PIN / Password", type="password")
            totp_secret = st.text_input("Long TOTP Secret Key", type="password")

        submit = st.form_submit_button("🚀 Start Live Scanner")

        if submit:
            if api_key and client_code and password and totp_secret:
                try:
                    current_totp = pyotp.TOTP(totp_secret).now()
                    smartApi = SmartConnect(api_key=api_key)
                    auth_data = smartApi.generateSession(client_code, password, current_totp)
                    
                    if auth_data.get('status') == True:
                        st.session_state['authenticated'] = True
                        st.rerun()
                    else:
                        st.error("❌ लॉगिन विफल। डिटेल्स चेक करें।")
                except Exception as e:
                    st.error(f"❌ एरर: {str(e)}")
            else:
                st.warning("⚠️ सभी फील्ड्स भरें!")

# ==========================================
# 4. MAIN ALGO DASHBOARD
# ==========================================
else:
    # 5 Min Auto-Refresh
    st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")

    st.title("⚡ Shahrukh Algo - Intraday Live Scanner")
    st.caption("15-Min ORB + VWAP + 10 EMA + Volume Filter (Strict Mode)")

    # --- ADVANCED RISK SELECTOR BUTTONS ---
    st.markdown("### 💰 प्रति ट्रेड रिस्क (Risk Amount) चुनें:")
    selected_risk = st.radio(
        "", 
        options=[250, 500, 750, 1000, 1500, 2000],
        index=3,
        horizontal=True,
        help="इस रिस्क अमाउंट के आधार पर क्वांटिटी और मार्जिन कैलकुलेट होगा।"
    )
    
    leverage = 5 # 5x Intraday Leverage

    st.markdown("---")

    # ==========================================
    # 5. STRICT ALGO LOGIC (As per Pine Script)
    # ==========================================
    # यह डेटा अब स्ट्रिक्ट लॉजिक को टेस्ट करने के लिए सेट किया गया है।
    # लाइव मार्केट में यहाँ Angel One API से डेटा आएगा।
    live_market_data = [
        {
            "Symbol": "SUZLON", 
            "LTP": 65.50, # Current Candle Close
            "Open_Price": 64.00,
            "15M_ORB_High": 64.80, # ORB High (15 min)
            "15M_ORB_Low": 63.50,
            "VWAP": 64.20, 
            "EMA_10": 64.50, 
            "RVOL": 2.1,
            "ATR": 0.50
        },
        {
            "Symbol": "TATASTEEL", 
            "LTP": 142.10, 
            "Open_Price": 141.50,
            "15M_ORB_High": 143.00, # LTP is below ORB High - (ये फ़िल्टर हो जाएगा, नहीं दिखेगा)
            "15M_ORB_Low": 140.50,
            "VWAP": 141.80, 
            "EMA_10": 142.00, 
            "RVOL": 1.2,
            "ATR": 1.10
        },
        {
            "Symbol": "IRFC", 
            "LTP": 152.30, 
            "Open_Price": 150.00,
            "15M_ORB_High": 151.00, 
            "15M_ORB_Low": 149.00,
            "VWAP": 150.10, 
            "EMA_10": 150.80, 
            "RVOL": 2.5,
            "ATR": 1.80
        }
    ]

    processed_table = []
    current_time = datetime.now().strftime("%H:%M:%S")

    for item in live_market_data:
        ltp = item["LTP"]
        orb_high = item["15M_ORB_High"]
        
        # Pine Script Filters: 
        # 1. isGreenCandle (LTP > Open)
        # 2. Breakout (LTP > ORB High)
        # 3. Indicators (LTP > VWAP & LTP > 10 EMA)
        # 4. Volume (RVOL >= 1.5)
        is_green = ltp > item["Open_Price"]
        is_breakout_buy = ltp > orb_high
        is_above_indicators = (ltp > item["VWAP"]) and (ltp > item["EMA_10"])
        has_volume = item["RVOL"] >= 1.5
        
        # STRICT CONDITION CHECK
        if (50 <= ltp <= 900) and is_green and is_breakout_buy and is_above_indicators and has_volume:
            
            # --- PINE SCRIPT CALCULATION LOGIC ---
            # SL = min(Current Low, Close - ATR). For scanner, we use LTP - ATR buffer.
            sl_price = round(ltp - item["ATR"], 2)
            
            risk_points = round(abs(ltp - sl_price), 2)
            
            if risk_points > 0:
                # Qty = Risk Amount / Risk Points
                qty = math.floor(selected_risk / risk_points)
                
                if qty > 0:
                    # Capital Required (5x Leverage) = (Qty * LTP) / 5
                    trade_value = qty * ltp
                    capital_req = math.ceil(trade_value / leverage)
                    
                    # Target (1:1.5)
                    reward_pts = round(risk_points * 1.5, 2)
                    target_price = round(ltp + reward_pts, 2)
                    
                    processed_table.append({
                        "Time": current_time,
                        "Stock": item["Symbol"],
                        "Signal": "🟢 BUY",
                        "Entry Price": ltp,
                        "Stop Loss": sl_price,
                        "Risk Amount": f"₹ {selected_risk}",
                        "Qty (Shares)": qty,
                        "Capital Req (5x)": f"₹ {capital_req:,}",
                        "Target (1.5x)": target_price,
                        "Chart": f"https://in.tradingview.com/chart/?symbol=NSE:{item['Symbol']}&interval=5"
                    })

    # ==========================================
    # 6. DISPLAY DASHBOARD
    # ==========================================
    st.subheader(f"🎯 Verified Breakouts ({len(processed_table)})")
    
    if processed_table:
        df = pd.DataFrame(processed_table)
        df = df.sort_values(by="Time", ascending=False)
        
        st.dataframe(
            df,
            column_config={
                "Chart": st.column_config.LinkColumn(
                    "TradingView 📈", 
                    display_text="Open 5-Min Chart"
                ),
                "Signal": st.column_config.TextColumn("Signal", width="small")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("⏳ फिलहाल कोई स्टॉक 15-Min ORB ब्रेकआउट और आपके इंडिकेटर के रूल्स को पास नहीं कर रहा है।")
