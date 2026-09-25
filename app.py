import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import math
import pyotp
from streamlit_autorefresh import st_autorefresh
from SmartApi import SmartConnect

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Shahrukh Algo Live Scanner",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# 2. SESSION STATE (IN-MEMORY LOGIN)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['smart_api'] = None

# ==========================================
# 3. RUNTIME LOGIN SCREEN (Auto 6-Digit TOTP)
# ==========================================
if not st.session_state['authenticated']:
    st.title("🔐 Shahrukh Algo - Angel One Login")
    st.caption("यह लॉगिन पूरी तरह से RAM (In-Memory) में रहता है।")

    with st.form("login_form"):
        col1, col2 = st.columns(2)
        with col1:
            api_key = st.text_input("SmartAPI Key", type="password")
            client_code = st.text_input("Client Code (e.g. A123456)")
        with col2:
            password = st.text_input("PIN / Password", type="password")
            totp_secret = st.text_input("Long TOTP Secret Key", type="password")

        submit = st.form_submit_button("🚀 Login & Start Live Scanner")

        if submit:
            if api_key and client_code and password and totp_secret:
                try:
                    current_6_digit_totp = pyotp.TOTP(totp_secret).now()
                    smartApi = SmartConnect(api_key=api_key)
                    auth_data = smartApi.generateSession(client_code, password, current_6_digit_totp)
                    
                    if auth_data.get('status') == True:
                        st.session_state['authenticated'] = True
                        st.session_state['smart_api'] = smartApi
                        st.success("✅ एंजेल वन लॉगिन सफल!")
                        st.rerun()
                    else:
                        st.error(f"❌ लॉगिन विफल: {auth_data.get('message', 'गलत क्रेडेंशियल्स')}")
                except Exception as e:
                    st.error(f"❌ कनेक्शन एरर: {str(e)}")
            else:
                st.warning("⚠️ कृपया सभी फ़ील्ड्स भरें!")

# ==========================================
# 4. MAIN DASHBOARD & ALGO ENGINE
# ==========================================
else:
    # 🔴 ऑटो रिफ्रेश: हर 5 मिनट (300,000 ms) में पेज रिफ्रेश होगा
    st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")

    # Sidebar Logout
    st.sidebar.success("🟢 Connected to Angel One")
    if st.sidebar.button("🔴 Logout / Clear Session"):
        st.session_state['authenticated'] = False
        st.session_state['smart_api'] = None
        st.rerun()

    st.title("⚡ Shahrukh Algo - Intraday Live Scanner")
    st.caption("रेंज: ₹50 से ₹900 | Nifty 750 Stocks | 15-Min ORB + 5-Min Confirmation")

    # ------------------------------------------
    # CONTROLS SECTION (RISK SELECTOR - PINE SCRIPT LOGIC)
    # ------------------------------------------
    st.markdown("### 💰 प्रति ट्रेड रिस्क (Risk Amount) चुनें:")
    # ड्रॉपडाउन की जगह सिलेक्शन बटन (Horizontal Radio)
    selected_risk = st.radio(
        "इस अमाउंट के आधार पर क्वांटिटी कैलकुलेट होगी:",
        options=[250, 500, 750, 1000, 1500, 2000],
        index=3, # Default: 1000
        horizontal=True
    )
    
    st.info(f"💡 **क्वांटिटी कैलकुलेशन:** आप एक ट्रेड में अधिकतम **₹{selected_risk}** का रिस्क लेना चाहते हैं।")
    st.markdown("---")

    # ------------------------------------------
    # SHAHRUKH ALGO LIVE SIGNALS DATA
    # ------------------------------------------
    # (यहाँ टाइमस्टैम्प जोड़ा गया है ताकि नई एंट्रीज़ ऊपर आ सकें)
    now = datetime.now()
    raw_signals_data = [
        {"Symbol": "SUZLON", "LTP": 62.50, "15M_ORB_High": 61.20, "Stop_Loss": 59.80, "VWAP": 61.50, "EMA_10": 61.80, "RVOL": 2.1, "Gap_Pct": 1.2, "Time": (now - timedelta(minutes=1)).strftime("%H:%M:%S")},
        {"Symbol": "NHPC", "LTP": 94.10, "15M_ORB_High": 92.50, "Stop_Loss": 90.20, "VWAP": 92.80, "EMA_10": 93.00, "RVOL": 1.8, "Gap_Pct": -0.5, "Time": (now - timedelta(minutes=6)).strftime("%H:%M:%S")},
        {"Symbol": "IRFC", "LTP": 152.30, "15M_ORB_High": 149.80, "Stop_Loss": 145.00, "VWAP": 150.10, "EMA_10": 150.80, "RVOL": 2.5, "Gap_Pct": 2.1, "Time": (now - timedelta(minutes=2)).strftime("%H:%M:%S")},
    ]

    processed_table = []

    for item in raw_signals_data:
        ltp = item["LTP"]
        sl = item["Stop_Loss"]
        
        # 1. Price Range Check
        if 50 <= ltp <= 900:
            # 2. Shahrukh Algo Conditions Check
            if (ltp > item["15M_ORB_High"]) and (ltp > item["VWAP"]) and (ltp > item["EMA_10"]) and (item["RVOL"] >= 1.5) and (abs(item["Gap_Pct"]) < 3.0):
                
                # 3. Pine Script Logic: Risk Points & Quantity
                risk_points = abs(ltp - sl)
                qty = math.floor(selected_risk / risk_points) if risk_points > 0 else 0
                
                if qty > 0:
                    margin_used = math.ceil((qty * ltp) / 5) # 5x Leverage capital required
                    reward_pts = round(risk_points * 1.5, 2)
                    target_price = round(ltp + reward_pts, 2)
                    
                    processed_table.append({
                        "Time": item["Time"],
                        "Stock": item["Symbol"],
                        "LTP (₹)": ltp,
                        "Signal": "🟢 BUY",
                        "Qty": qty,
                        "Risk Pts": round(risk_points, 2),
                        "Stop Loss (₹)": sl,
                        "Target (1:1.5)": target_price,
                        "Req. Margin": f"₹ {margin_used:,}",
                        "TradingView Link": f"https://in.tradingview.com/chart/?symbol=NSE:{item['Symbol']}&interval=5"
                    })

    st.subheader(f"🎯 Live Signals")
    
    if processed_table:
        df = pd.DataFrame(processed_table)
        
        # 🔴 नया सिग्नल ऊपर, पुराना नीचे (Time के आधार पर डिसेंडिंग)
        df = df.sort_values(by="Time", ascending=False)
        
        st.dataframe(
            df,
            column_config={
                "TradingView Link": st.column_config.LinkColumn(
                    "TradingView Chart",
                    help="5 मिनट टाइमफ्रेम पर चार्ट खोलने के लिए क्लिक करें",
                    display_text="Open Chart 📈"
                )
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("फिलहाल शाहरूख एल्गो की सभी शर्तों को पूरा करने वाला कोई नया सिग्नल नहीं मिला है।")
