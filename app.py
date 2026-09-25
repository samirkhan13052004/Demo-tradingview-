import streamlit as st
import pandas as pd
import requests
import datetime
import math
import pyotp
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
    st.caption("यह लॉगिन पूरी तरह से RAM (In-Memory) में रहता है। ब्राउज़र टैब बंद करते ही डेटा मिट जाएगा।")

    with st.form("login_form"):
        col1, col2 = st.columns(2)
        with col1:
            api_key = st.text_input("SmartAPI Key", type="password")
            client_code = st.text_input("Client Code (e.g. A123456)")
        with col2:
            password = st.text_input("PIN / Password", type="password")
            # यहाँ आपको अपना लंबा वाला TOTP Secret डालना है
            totp_secret = st.text_input("Long TOTP Secret Key", type="password", help="अपना लंबा वाला TOTP सीक्रेट यहाँ डालें")

        submit = st.form_submit_button("🚀 Login & Start Live Scanner")

        if submit:
            if api_key and client_code and password and totp_secret:
                try:
                    # pyotp आपके लंबे सीक्रेट से लाइव 6-अंकीय कोड बनाएगा
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
                st.warning("⚠️ कृपया सभी 4 फ़ील्ड्स सही से भरें!")

# ==========================================
# 4. MAIN DASHBOARD & ALGO ENGINE
# ==========================================
else:
    # Sidebar Logout
    st.sidebar.success("🟢 Connected to Angel One")
    if st.sidebar.button("🔴 Logout / Clear Session"):
        st.session_state['authenticated'] = False
        st.session_state['smart_api'] = None
        st.rerun()

    st.title("⚡ Shahrukh Algo - Intraday Live Scanner")
    st.caption("रेंज: ₹50 से ₹900 | Nifty 750 Stocks | 15-Min ORB + 5-Min Confirmation | 5x Leverage Sizing")

    # ------------------------------------------
    # CONTROLS SECTION (RISK & LEVERAGE SELECTOR)
    # ------------------------------------------
    col_risk, col_info = st.columns([1, 2])
    
    with col_risk:
        selected_capital = st.selectbox(
            "💰 अपना मार्जिन (Capital) चुनें (₹):",
            options=[250, 500, 750, 1000, 1500, 2000],
            index=3, # Default: ₹1000
            help="चयनित मार्जिन राशि पर 5x लिवरेज लागू होगा।"
        )
    
    buying_power = selected_capital * 5

    with col_info:
        st.info(
            f"💡 **लिवरेज कैलकुलेशन (5x Margin):**\n\n"
            f"• आपका मार्जिन: **₹{selected_capital:,}** | "
            f"• कुल बाइंग पावर (5x Exposure): **₹{buying_power:,}**"
        )

    st.markdown("---")

    # ------------------------------------------
    # SHAHRUKH ALGO LIVE SIGNALS DATA (MOCK LIVE DATA)
    # ------------------------------------------
    raw_signals_data = [
        {
            "Symbol": "SUZLON",
            "LTP": 62.50,
            "15M_ORB_High": 61.20,
            "Stop_Loss": 59.80,
            "VWAP": 61.50,
            "EMA_10": 61.80,
            "RVOL": 2.1,
            "Gap_Pct": 1.2
        },
        {
            "Symbol": "NHPC",
            "LTP": 94.10,
            "15M_ORB_High": 92.50,
            "Stop_Loss": 90.20,
            "VWAP": 92.80,
            "EMA_10": 93.00,
            "RVOL": 1.8,
            "Gap_Pct": -0.5
        },
        {
            "Symbol": "IRFC",
            "LTP": 152.30,
            "15M_ORB_High": 149.80,
            "Stop_Loss": 145.00,
            "VWAP": 150.10,
            "EMA_10": 150.80,
            "RVOL": 2.5,
            "Gap_Pct": 2.1
        },
        {
            "Symbol": "BHEL",
            "LTP": 285.00,
            "15M_ORB_High": 280.00,
            "Stop_Loss": 274.00,
            "VWAP": 281.20,
            "EMA_10": 282.50,
            "RVOL": 1.9,
            "Gap_Pct": 0.8
        },
        {
            "Symbol": "TATAMOTORS",
            "LTP": 875.00,
            "15M_ORB_High": 862.00,
            "Stop_Loss": 845.00,
            "VWAP": 864.50,
            "EMA_10": 866.00,
            "RVOL": 1.6,
            "Gap_Pct": 1.5
        }
    ]

    # Dynamic Quantity & Risk Processing based on Dropdown
    processed_table = []

    for item in raw_signals_data:
        ltp = item["LTP"]
        sl = item["Stop_Loss"]
        
        # 1. Price Range Check (₹50 to ₹900)
        if 50 <= ltp <= 900:
            # 2. Shahrukh Algo Conditions Check
            if (ltp > item["15M_ORB_High"]) and (ltp > item["VWAP"]) and (ltp > item["EMA_10"]) and (item["RVOL"] >= 1.5) and (abs(item["Gap_Pct"]) < 3.0):
                
                # 3. Dynamic Leverage Quantity Calculation (5x Buying Power)
                qty = math.floor(buying_power / ltp)
                
                if qty > 0:
                    margin_used = math.ceil((qty * ltp) / 5)
                    max_risk_amt = round(qty * (ltp - sl), 2)
                    reward_pts = round((ltp - sl) * 1.5, 2)
                    target_price = round(ltp + reward_pts, 2)
                    
                    processed_table.append({
                        "Stock": item["Symbol"],
                        "LTP (₹)": ltp,
                        "Signal": "🟢 BUY",
                        "Qty (5x)": qty,
                        "Required Margin": f"₹ {margin_used:,}",
                        "Stop Loss (₹)": sl,
                        "Target (1:1.5)": target_price,
                        "Max Risk (SL)": f"₹ {max_risk_amt:,}",
                        "RVOL": f"{item['RVOL']}x",
                        "TradingView Link": f"https://in.tradingview.com/chart/?symbol=NSE:{item['Symbol']}"
                    })

    # Display Results
    st.subheader(f"🎯 Verified Signals ({len(processed_table)})")
    
    if processed_table:
        df = pd.DataFrame(processed_table)
        
        st.dataframe(
            df,
            column_config={
                "TradingView Link": st.column_config.LinkColumn(
                    "TradingView Chart",
                    help="Click to open chart with Shahrukh Algo Indicator",
                    display_text="Open Chart 📈"
                )
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("फिलहाल शाहरूख एल्गो की सभी शर्तों को पूरा करने वाला कोई स्टॉक नहीं मिला है।")
