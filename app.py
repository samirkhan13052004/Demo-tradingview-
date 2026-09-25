import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math
import pyotp
from SmartApi import SmartConnect

# ==========================================
# 1. PAGE CONFIG & 100% MATCHING CSS (AS PER 11867.jpg)
# ==========================================
st.set_page_config(page_title="Shahrukh Algo PRO", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Base Background */
    .stApp { background-color: #f2f2f7; font-family: -apple-system, sans-serif; }
    
    /* Title and Subtitle */
    .title { text-align: center; font-size: 36px; font-weight: 900; color: #000; margin-bottom: 5px; margin-top: 10px; }
    .subtitle { text-align: center; color: #6e6e73; font-weight: 600; font-size: 14px; margin-bottom: 30px; letter-spacing: 0.5px; }
    
    /* Login Page Input Boxes */
    div[data-testid="stTextInput"] input {
        background-color: #fff !important;
        border: 1px solid #e5e5ea !important;
        border-radius: 10px !important;
        color: #000 !important;
        font-weight: 600 !important;
        padding: 12px 15px !important;
    }
    
    /* Pink Refresh / Submit Button (As seen in image) */
    div[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(90deg, #ff416c, #ff4b2b) !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        letter-spacing: 1px !important;
        border-radius: 12px !important;
        padding: 12px !important;
        border: none !important;
        box-shadow: 0px 8px 15px rgba(255, 65, 108, 0.3) !important;
        text-transform: uppercase !important;
        width: 100% !important;
        margin-top: 10px !important;
    }
    
    /* Table Styling (Clean White Card) */
    .table-card { background: #fff; border-radius: 16px; padding: 2px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e5e5ea; }
    .algo-table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 16px; overflow: hidden; }
    .algo-table th { font-size: 11px; color: #8e8e93; text-transform: uppercase; padding: 15px 10px; text-align: center; font-weight: 800; background: #f9f9f9; border-bottom: 1px solid #eee; }
    .algo-table td { font-size: 14px; font-weight: 700; padding: 15px 10px; text-align: center; color: #1c1c1e; border-bottom: 1px solid #f9f9f9; }
    
    /* Text Colors */
    .t-buy { color: #00c853 !important; font-weight: 900; }
    .t-sell { color: #ff3d00 !important; font-weight: 900; }
    .t-blue { color: #2962ff !important; font-weight: 900; }
    .t-action { background: #1c1c1e; color: white !important; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CLEAN LOGIN PAGE (WHITE BACKGROUND FIXED)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['smartApi'] = None

if not st.session_state['authenticated']:
    st.markdown('<div class="title">Scanner Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Connect your Angel One API</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            api_key = st.text_input("SmartAPI Key", type="password")
            client_code = st.text_input("Client Code")
            password = st.text_input("Angel One PIN", type="password")
            totp_secret = st.text_input("TOTP Secret", type="password")
            
            submitted = st.form_submit_button("LOGIN TO SCANNER")
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
# 3. LIVE SCANNER (5-MIN DATA + BUY/SELL LOGIC)
# ==========================================
else:
    st.markdown('<div class="title">Shahrukh Algo Scanner</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">15-Min ORB • VWAP • 10 EMA • Live Angel One Data</div>', unsafe_allow_html=True)
    
    # Risk selection (Matching image layout)
    risk_options = [250, 500, 750, 1000, 1500, 2000]
    selected_risk = st.radio("Risk:", options=risk_options, index=3, horizontal=True, label_visibility="collapsed")
    leverage = 5 
    
    # Top 20 Liquid Stocks with actual Angel One Tokens
    STOCK_LIST = {
        "RELIANCE": "2885", "HDFCBANK": "1333", "ICICIBANK": "4963", "SBIN": "43", 
        "TCS": "11536", "INFY": "1594", "ITC": "1660", "LT": "11483", "KOTAKBANK": "1922", 
        "AXISBANK": "5900", "TATAMOTORS": "3456", "MARUTI": "10999", "SUNPHARMA": "3351", 
        "TATASTEEL": "3499", "BAJFINANCE": "317", "M&M": "2031", "ASIANPAINT": "236", 
        "HCLTECH": "7229", "TITAN": "3506", "NTPC": "11630"
    }
    
    smartApi = st.session_state['smartApi']
    current_time = datetime.now().strftime("%I:%M %p")
    
    # We fetch 5-Minute interval data for the last 4 days to calculate EMA properly
    to_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    from_date = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d 09:15")
    
    processed_signals = []
    
    with st.spinner("Fetching 5-Min live data..."):
        for symbol, token in STOCK_LIST.items():
            try:
                historicParam = {
                    "exchange": "NSE",
                    "symboltoken": token,
                    "interval": "FIVE_MINUTE",
                    "fromdate": from_date,
                    "todate": to_date
                }
                api_response = smartApi.getCandleData(historicParam)
                
                if api_response and api_response.get("status") and api_response.get("data"):
                    cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                    df = pd.DataFrame(api_response["data"], columns=cols)
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col])
                        
                    df['Date'] = pd.to_datetime(df['timestamp']).dt.date
                    df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
                    
                    today = df['Date'].iloc[-1]
                    today_df = df[df['Date'] == today].copy()
                    
                    if len(today_df) > 0:
                        # 1. VWAP Calculation
                        today_df['Typ_Price'] = (today_df['high'] + today_df['low'] + today_df['close']) / 3
                        today_df['Cum_Vol_Price'] = (today_df['Typ_Price'] * today_df['volume']).cumsum()
                        today_df['Cum_Vol'] = today_df['volume'].cumsum()
                        today_df['VWAP'] = today_df['Cum_Vol_Price'] / today_df['Cum_Vol']
                        
                        # 2. 15-Min ORB (First 3 candles of 5-min timeframe)
                        orb_high = today_df['high'].iloc[0:3].max() if len(today_df) >= 3 else today_df['high'].max()
                        orb_low = today_df['low'].iloc[0:3].min() if len(today_df) >= 3 else today_df['low'].min()
                        
                        latest = today_df.iloc[-1]
                        ltp = latest['close']
                        vwap = latest['VWAP']
                        ema_10 = latest['EMA_10']
                        
                        signal_type = None
                        
                        # BUY CONDITIONS
                        if (ltp > orb_high) and (ltp > latest['open']) and (ltp > vwap) and (ltp > ema_10):
                            signal_type = "BUY"
                            sl_price = latest['low'] - 1 # SL at current candle low
                            
                        # SELL CONDITIONS (Added to ensure you get trades in down market)
                        elif (ltp < orb_low) and (ltp < latest['open']) and (ltp < vwap) and (ltp < ema_10):
                            signal_type = "SELL"
                            sl_price = latest['high'] + 1 # SL at current candle high
                            
                        if signal_type:
                            risk_points = round(abs(ltp - sl_price), 2)
                            if risk_points > 0:
                                qty = math.floor(selected_risk / risk_points)
                                if qty > 0:
                                    margin = math.ceil((qty * ltp) / leverage)
                                    target = round(ltp + (risk_points * 1.5), 2) if signal_type == "BUY" else round(ltp - (risk_points * 1.5), 2)
                                    
                                    processed_signals.append({
                                        "Time": current_time, "Stock": symbol, "Signal": signal_type,
                                        "Entry": ltp, "SL": sl_price, "Qty": qty, "Margin": margin, "Target": target
                                    })
            except Exception:
                pass # Skip if API fails for one stock

    # ==========================================
    # 4. 100% BUG-FREE HTML RENDER (ONE-LINE STRING)
    # ==========================================
    if processed_signals:
        # NOTICE: NO INDENTATION OR NEWLINES HERE to prevent the black code block bug!
        html_str = "<div class='table-card'><table class='algo-table'><thead><tr><th>Time</th><th>Stock</th><th>Signal</th><th>Entry (₹)</th><th>Stop Loss</th><th>Quantity</th><th>Margin (5x)</th><th>Target (1.5x)</th><th>Action</th></tr></thead><tbody>"
        
        for sig in processed_signals:
            c_sig = "t-buy" if sig["Signal"] == "BUY" else "t-sell"
            tv_link = f"https://in.tradingview.com/chart/?symbol=NSE:{sig['Stock']}&interval=5"
            html_str += f"<tr><td style='color:#6e6e73;'>{sig['Time']}</td><td style='font-weight:900;'>{sig['Stock']}</td><td class='{c_sig}'>{sig['Signal']}</td><td class='t-blue'>{sig['Entry']:.2f}</td><td class='{c_sig}'>{sig['SL']:.2f}</td><td>{sig['Qty']}</td><td style='color:#000;'>₹{sig['Margin']:,}</td><td class='{c_sig}'>{sig['Target']:.2f}</td><td><a href='{tv_link}' target='_blank' class='t-action'>CHART</a></td></tr>"
            
        html_str += "</tbody></table></div>"
        
        # Render HTML
        st.markdown(html_str, unsafe_allow_html=True)
    else:
        st.markdown("<div class='table-card' style='padding: 30px; text-align: center;'><h3 style='color:#6e6e73;'>⏳ Scanning... No ORB Breakout in Top 20 Stocks right now.</h3></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # The Pink Button exactly as in the image
    if st.button("REFRESH LIVE SCANNER"):
        st.rerun()
