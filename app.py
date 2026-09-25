import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
import pyotp
from SmartApi import SmartConnect

# ==========================================
# 1. PAGE CONFIG & 100% MATCHING CSS 
# ==========================================
st.set_page_config(page_title="Shahrukh Algo PRO", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #f2f2f7; font-family: -apple-system, sans-serif; }
    .title { text-align: center; font-size: 36px; font-weight: 900; color: #000; margin-bottom: 5px; margin-top: 10px; }
    .subtitle { text-align: center; color: #6e6e73; font-weight: 600; font-size: 14px; margin-bottom: 30px; letter-spacing: 0.5px; }
    div[data-testid="stTextInput"] input { background-color: #fff !important; border: 1px solid #e5e5ea !important; border-radius: 10px !important; color: #000 !important; font-weight: 600 !important; padding: 12px 15px !important; }
    div[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button { background: linear-gradient(90deg, #ff416c, #ff4b2b) !important; color: white !important; font-weight: 800 !important; font-size: 16px !important; letter-spacing: 1px !important; border-radius: 12px !important; padding: 12px !important; border: none !important; box-shadow: 0px 8px 15px rgba(255, 65, 108, 0.3) !important; text-transform: uppercase !important; width: 100% !important; margin-top: 10px !important; }
    .table-card { background: #fff; border-radius: 16px; padding: 2px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e5e5ea; }
    .algo-table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 16px; overflow: hidden; }
    .algo-table th { font-size: 11px; color: #8e8e93; text-transform: uppercase; padding: 15px 10px; text-align: center; font-weight: 800; background: #f9f9f9; border-bottom: 1px solid #eee; }
    .algo-table td { font-size: 14px; font-weight: 700; padding: 15px 10px; text-align: center; color: #1c1c1e; border-bottom: 1px solid #f9f9f9; }
    .t-buy { color: #00c853 !important; font-weight: 900; }
    .t-sell { color: #ff3d00 !important; font-weight: 900; }
    .t-blue { color: #2962ff !important; font-weight: 900; }
    .t-action { background: #1c1c1e; color: white !important; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIN PAGE 
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
# 3. PINE SCRIPT LOGIC REPLICATION
# ==========================================
else:
    st.markdown('<div class="title">Shahrukh Algo Scanner</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Pine Script v6 Logic: RVOL, ATR, ORB, Gap Filters Applied</div>', unsafe_allow_html=True)
    
    risk_options = [250, 500, 750, 1000, 1500, 2000]
    selected_risk = st.radio("Risk:", options=risk_options, index=3, horizontal=True, label_visibility="collapsed")
    
    # Pine Script Settings
    leverage = 5 
    max_gap_pct = 3.0
    max_first_candle_pct = 1.5
    rvol_threshold = 1.5
    min_rr = 1.5
    
    STOCK_LIST = {
        "RELIANCE": "2885", "HDFCBANK": "1333", "ICICIBANK": "4963", "SBIN": "43", 
        "TCS": "11536", "INFY": "1594", "ITC": "1660", "LT": "11483", "KOTAKBANK": "1922", 
        "AXISBANK": "5900", "TATAMOTORS": "3456", "MARUTI": "10999", "SUNPHARMA": "3351", 
        "TATASTEEL": "3499", "BAJFINANCE": "317", "M&M": "2031", "ASIANPAINT": "236", 
        "HCLTECH": "7229", "TITAN": "3506", "NTPC": "11630"
    }
    
    smartApi = st.session_state['smartApi']
    current_time = datetime.now().strftime("%I:%M %p")
    
    # We fetch 6 days of data to properly calculate Volume SMA(20) and ATR(14)
    to_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    from_date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d 09:15")
    
    processed_signals = []
    
    with st.spinner("Applying Pine Script logic... Please wait."):
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
                    
                    # 1. EMA 10
                    df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
                    
                    # 2. RVOL (SMA 20)
                    df['vol_sma_20'] = df['volume'].rolling(window=20).mean()
                    df['rvol'] = df['volume'] / df['vol_sma_20']
                    
                    # 3. ATR 14
                    df['prev_close'] = df['close'].shift(1)
                    df['tr'] = df[['high', 'low', 'prev_close']].apply(
                        lambda x: max(x['high'] - x['low'], abs(x['high'] - x['prev_close']), abs(x['low'] - x['prev_close'])), axis=1
                    )
                    df['atr'] = df['tr'].ewm(alpha=1/14, adjust=False).mean() # RMA calculation equivalent
                    
                    # Focus on Today's Data
                    today = df['Date'].iloc[-1]
                    today_df = df[df['Date'] == today].copy()
                    
                    # Previous day's close for Gap % calculation
                    prev_days = df[df['Date'] < today]
                    if prev_days.empty or today_df.empty or len(today_df) <= 3:
                        continue # Skip if not enough data or ORB not formed
                        
                    prev_day_close = prev_days.iloc[-1]['close']
                    first_candle = today_df.iloc[0]
                    
                    # Filter: Gap & 1st Candle Size
                    gap_pct = (abs(first_candle['open'] - prev_day_close) / prev_day_close) * 100
                    candle_pct = (abs(first_candle['high'] - first_candle['low']) / first_candle['open']) * 100
                    
                    if gap_pct >= max_gap_pct or candle_pct >= max_first_candle_pct:
                        continue # isDayValid = false logic
                        
                    # 4. VWAP Calculation
                    today_df['Typ_Price'] = (today_df['high'] + today_df['low'] + today_df['close']) / 3
                    today_df['Cum_Vol_Price'] = (today_df['Typ_Price'] * today_df['volume']).cumsum()
                    today_df['Cum_Vol'] = today_df['volume'].cumsum()
                    today_df['VWAP'] = today_df['Cum_Vol_Price'] / today_df['Cum_Vol']
                    
                    # 5. ORB (First 3 candles = 15 Mins)
                    orb_high = today_df['high'].iloc[0:3].max()
                    orb_low = today_df['low'].iloc[0:3].min()
                    orb_range = orb_high - orb_low
                    
                    # Evaluate Latest Candle
                    latest = today_df.iloc[-1]
                    ltp = latest['close']
                    vwap = latest['VWAP']
                    ema_10 = latest['EMA_10']
                    atr_val = latest['atr']
                    rvol_val = latest['rvol']
                    
                    is_green = latest['close'] > latest['open']
                    is_red = latest['close'] < latest['open']
                    
                    signal_type = None
                    sl_price = 0
                    
                    # potential risk & expected RR
                    pot_buy_sl = min(latest['low'], ltp - atr_val)
                    risk_buy = ltp - pot_buy_sl
                    exp_rr_buy = (orb_range / risk_buy) if risk_buy > 0 else 0
                    
                    pot_sell_sl = max(latest['high'], ltp + atr_val)
                    risk_sell = pot_sell_sl - ltp
                    exp_rr_sell = (orb_range / risk_sell) if risk_sell > 0 else 0
                    
                    # 6. PINE SCRIPT BUY/SELL CONDITIONS
                    # BUY
                    if (ltp > orb_high) and (ltp > vwap) and is_green and (rvol_val >= rvol_threshold) and (exp_rr_buy >= min_rr):
                        signal_type = "BUY"
                        sl_price = pot_buy_sl
                        
                    # SELL
                    elif (ltp < orb_low) and (ltp < vwap) and is_red and (rvol_val >= rvol_threshold) and (exp_rr_sell >= min_rr):
                        signal_type = "SELL"
                        sl_price = pot_sell_sl
                        
                    if signal_type:
                        risk_points = round(abs(ltp - sl_price), 2)
                        if risk_points > 0:
                            qty = math.floor(selected_risk / risk_points)
                            if qty > 0:
                                margin = math.ceil((qty * ltp) / leverage)
                                target = round(ltp + (risk_points * min_rr), 2) if signal_type == "BUY" else round(ltp - (risk_points * min_rr), 2)
                                
                                processed_signals.append({
                                    "Time": current_time, "Stock": symbol, "Signal": signal_type,
                                    "Entry": ltp, "SL": round(sl_price, 2), "Qty": qty, "Margin": margin, "Target": target
                                })
            except Exception:
                pass 

    # ==========================================
    # 4. SINGLE LINE HTML RENDER (UI BUG FIXED)
    # ==========================================
    if processed_signals:
        html_str = "<div class='table-card'><table class='algo-table'><thead><tr><th>Time</th><th>Stock</th><th>Signal</th><th>Entry (₹)</th><th>Stop Loss</th><th>Quantity</th><th>Margin (5x)</th><th>Target</th><th>Action</th></tr></thead><tbody>"
        for sig in processed_signals:
            c_sig = "t-buy" if sig["Signal"] == "BUY" else "t-sell"
            tv_link = f"https://in.tradingview.com/chart/?symbol=NSE:{sig['Stock']}&interval=5"
            html_str += f"<tr><td style='color:#6e6e73;'>{sig['Time']}</td><td style='font-weight:900;'>{sig['Stock']}</td><td class='{c_sig}'>{sig['Signal']}</td><td class='t-blue'>{sig['Entry']:.2f}</td><td class='{c_sig}'>{sig['SL']:.2f}</td><td>{sig['Qty']}</td><td style='color:#000;'>₹{sig['Margin']:,}</td><td class='{c_sig}'>{sig['Target']:.2f}</td><td><a href='{tv_link}' target='_blank' class='t-action'>CHART</a></td></tr>"
        html_str += "</tbody></table></div>"
        st.markdown(html_str, unsafe_allow_html=True)
    else:
        st.markdown("<div class='table-card' style='padding: 30px; text-align: center;'><h3 style='color:#6e6e73;'>⏳ Scanning... No strict Pine Script setups right now.</h3><p style='color:#8e8e93; font-size:12px;'>Waiting for RVOL > 1.5, R:R > 1.5, and ORB Breakout</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("REFRESH LIVE SCANNER"):
        st.rerun()
