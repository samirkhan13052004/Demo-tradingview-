import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math
import pyotp
from SmartApi import SmartConnect

# ==========================================
# 1. PAGE CONFIG & PROPER CSS FIXES
# ==========================================
st.set_page_config(page_title="Shahrukh Algo PRO", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* Base Theme */
    .stApp {
        background-color: #f2f2f7;
        background-image: 
            radial-gradient(circle at 15% 30%, rgba(0, 122, 255, 0.08), transparent 50%),
            radial-gradient(circle at 85% 20%, rgba(52, 199, 89, 0.08), transparent 50%);
        background-attachment: fixed;
    }
    
    /* Text Color Fixes (White on White issue resolved) */
    p, h1, h2, h3, h4, h5, h6, label, span {
        color: #1c1c1e !important; 
    }
    
    /* Login Card Styling */
    [data-testid="stForm"] {
        background: #ffffff;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Input Boxes Styling */
    div[data-testid="stTextInput"] input {
        background-color: #f9f9fb !important;
        border: 1.5px solid #e5e5ea !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #1c1c1e !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #007aff !important;
        box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.2) !important;
    }
    
    /* Form Submit Button (Calculator Theme) */
    [data-testid="stFormSubmitButton"] button, div[data-testid="stButton"] button {
        background: #f04770 !important;
        color: #ffffff !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 12px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        width: 100% !important;
        text-transform: uppercase !important;
        box-shadow: 0 8px 20px rgba(240, 71, 112, 0.3) !important;
    }
    [data-testid="stFormSubmitButton"] button p, div[data-testid="stButton"] button p {
        color: #ffffff !important; /* Force button text to be white */
    }
    
    /* Table Styling */
    .floating-table-card {
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.06);
        overflow: hidden;
        margin-top: 20px;
        border: 1px solid #e5e5ea;
    }
    .algo-table { width: 100%; border-collapse: collapse; }
    .algo-table th { background: #f9f9fb; color: #8e8e93; padding: 15px; text-align: center; font-size: 12px; font-weight: 800; text-transform: uppercase; border-bottom: 1px solid #e5e5ea; }
    .algo-table td { padding: 15px; color: #1c1c1e; text-align: center; border-bottom: 1px solid #f2f2f7; font-weight: 700; font-size: 15px; }
    .algo-table tr:hover { background: #f0f8ff; }
    
    /* Custom Colors */
    .c-buy { color: #34c759; font-weight: 900; }
    .c-sell { color: #ff3b30; font-weight: 900; }
    .c-blue { color: #007aff; font-weight: 900; }
    .tv-btn { background: #007aff; color: white !important; padding: 6px 14px; border-radius: 8px; text-decoration: none; font-size: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIN PAGE (NOW INSIDE A PROPER CARD)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['smartApi'] = None

if not st.session_state['authenticated']:
    st.markdown('<h1 style="text-align: center; font-weight: 900;">Scanner Login</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6e6e73 !important; font-weight: 600;">Connect your Angel One API</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        # Using st.form creates a natural card in Streamlit which we styled via CSS above
        with st.form("login_card"):
            api_key = st.text_input("SmartAPI Key", type="password")
            client_code = st.text_input("Client Code")
            password = st.text_input("Angel One PIN", type="password")
            totp_secret = st.text_input("TOTP Secret", type="password")
            
            submitted = st.form_submit_button("CONNECT & START")
            if submitted:
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
# 3. REAL LIVE SCANNER LOGIC (PROPER WORKING CODE)
# ==========================================
else:
    st.markdown('<h1 style="text-align: center; font-weight: 900;">Shahrukh Algo Scanner</h1>', unsafe_allow_html=True)
    
    # Selected Risk
    risk_options = [250, 500, 750, 1000, 1500, 2000]
    selected_risk = st.radio("Risk Per Trade (₹):", options=risk_options, index=3, horizontal=True)
    leverage = 5 

    st.write("🔄 Fetching Live Market Data from Angel One...")

    # 🔴 REAL STOCK TOKENS (Add your required NFO/NSE stock tokens here)
    # Format: {"STOCK_NAME": "TOKEN"}
    STOCK_LIST = {
        "RELIANCE": "2885", 
        "TCS": "11536", 
        "INFY": "1594", 
        "HDFCBANK": "1333",
        "ICICIBANK": "4963",
        "SBIN": "43",
        "TATAMOTORS": "3456",
        "ZOMATO": "5097" # You can add 50-100 stocks here
    }

    processed_signals = []
    smartApi = st.session_state['smartApi']
    current_time = datetime.now().strftime("%I:%M %p")
    
    # Calculate Date for API (Last 5 days for proper EMA/VWAP calculation)
    to_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    from_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M")

    # API FETCH LOOP
    for symbol, token in STOCK_LIST.items():
        try:
            historicParam = {
                "exchange": "NSE",
                "symboltoken": token,
                "interval": "FIFTEEN_MINUTE",
                "fromdate": from_date,
                "todate": to_date
            }
            api_response = smartApi.getCandleData(historicParam)
            
            if api_response.get("status") and api_response.get("data"):
                # Convert API data to Pandas DataFrame
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df = pd.DataFrame(api_response["data"], columns=columns)
                
                # Ensure numeric types
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col])
                
                # 1. Calculate 10 EMA
                df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
                
                # 2. Calculate VWAP (Intraday)
                df['Date'] = pd.to_datetime(df['timestamp']).dt.date
                today = df['Date'].iloc[-1]
                today_df = df[df['Date'] == today].copy()
                
                if not today_df.empty:
                    today_df['Typ_Price'] = (today_df['high'] + today_df['low'] + today_df['close']) / 3
                    today_df['Cum_Vol'] = today_df['volume'].cumsum()
                    today_df['Cum_Vol_Price'] = (today_df['Typ_Price'] * today_df['volume']).cumsum()
                    today_df['VWAP'] = today_df['Cum_Vol_Price'] / today_df['Cum_Vol']
                    
                    # 3. Calculate ORB (First 15 Min Candle High/Low of the day)
                    orb_high = today_df['high'].iloc[0]
                    orb_low = today_df['low'].iloc[0]
                    
                    # Latest Candle Data
                    latest = today_df.iloc[-1]
                    ltp = latest['close']
                    vwap = latest['VWAP']
                    ema_10 = latest['EMA_10']
                    
                    # ATR Logic (Simple High - Low of latest candle for Stoploss demo)
                    atr = latest['high'] - latest['low']
                    
                    # ==========================================
                    # YOUR BREAKOUT CONDITIONS
                    # ==========================================
                    cond_breakout = ltp > orb_high                    
                    cond_green = ltp > latest['open']                  
                    cond_indicators = (ltp > vwap) and (ltp > ema_10) 
                    
                    # If all conditions match, generate signal
                    if cond_breakout and cond_green and cond_indicators:
                        sl_price = round(ltp - (atr if atr > 0 else (ltp*0.01)), 2)
                        risk_points = round(abs(ltp - sl_price), 2)
                        
                        if risk_points > 0:
                            qty = math.floor(selected_risk / risk_points) 
                            if qty > 0:
                                margin = math.ceil((qty * ltp) / leverage) 
                                target = round(ltp + (risk_points * 1.5), 2) 
                                
                                processed_signals.append({
                                    "Time": current_time,
                                    "Stock": symbol,
                                    "Entry": ltp,
                                    "SL": sl_price,
                                    "Qty": qty,
                                    "Margin": margin,
                                    "Target": target
                                })
        except Exception as e:
            # If any stock fails, it skips to next
            pass

    # ==========================================
    # 4. RENDER FIX: CLEAN HTML TABLE
    # ==========================================
    if processed_signals:
        html = "<div class='floating-table-card'><table class='algo-table'>"
        html += "<thead><tr><th>Time</th><th>Stock</th><th>Signal</th><th>Entry (₹)</th><th>Stop Loss</th><th>Quantity</th><th>Margin</th><th>Target</th><th>Chart</th></tr></thead><tbody>"
        
        for sig in processed_signals:
            tv_link = f"https://in.tradingview.com/chart/?symbol=NSE:{sig['Stock']}&interval=5"
            html += f"<tr><td>{sig['Time']}</td><td style='font-weight:900;'>{sig['Stock']}</td><td class='c-buy'>BUY</td><td class='c-blue'>{sig['Entry']:.2f}</td><td class='c-sell'>{sig['SL']:.2f}</td><td style='font-weight:900;'>{sig['Qty']}</td><td>₹{sig['Margin']:,}</td><td class='c-buy'>{sig['Target']:.2f}</td><td><a href='{tv_link}' target='_blank' class='tv-btn'>VIEW</a></td></tr>"
        
        html += "</tbody></table></div>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("⏳ Waiting for setup... किसी भी स्टॉक ने अभी ORB/VWAP/10EMA ब्रेकआउट नहीं दिया है।")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("REFRESH SCANNER", use_container_width=True):
        st.rerun()
