import streamlit as st
import pandas as pd

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Shahrukh Algo Live Demo",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# 2. SESSION STATE (IN-MEMORY LOGIN)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# ==========================================
# 3. LOGIN SCREEN (क्रेडेंशियल्स कहीं सेव नहीं होंगे)
# ==========================================
if not st.session_state['authenticated']:
    st.title("🔐 Shahrukh Algo - Secure Login Demo")
    st.info("यह लॉगिन पूरी तरह से इन-मेमोरी (RAM) पर आधारित है। टैब बंद करते ही डेटा डिलीट हो जाएगा।")

    with st.form("login_form"):
        col1, col2 = st.columns(2)
        with col1:
            api_key = st.text_input("API Key", type="password", placeholder="अपनी Angel One API Key डालें")
            client_code = st.text_input("Client Code", placeholder="उदा. A123456")
        with col2:
            password = st.text_input("Password / PIN", type="password", placeholder="अपना Angel One PIN डालें")
            totp = st.text_input("Current TOTP", placeholder="6-अंकीय TOTP कोड")

        submit = st.form_submit_button("🚀 Start Demo Scanner")

        if submit:
            # केवल टेस्ट/डेमो के लिए: अगर कुछ भी टाइप किया है तो लॉगिन मान लिया जाएगा
            if api_key and client_code and password and totp:
                st.session_state['authenticated'] = True
                st.success("✅ लॉगिन सफल! डैशबोर्ड लोड हो रहा है...")
                st.rerun()
            else:
                st.error("⚠️ कृपया डेमो टेस्ट करने के लिए सभी चारों फ़ील्ड्स में कुछ भी टाइप करें।")

# ==========================================
# 4. MAIN DASHBOARD & TRADINGVIEW LINKS
# ==========================================
else:
    st.sidebar.success("🟢 Demo Scanner Active")
    if st.sidebar.button("🔴 Logout / Clear Session"):
        st.session_state['authenticated'] = False
        st.rerun()

    st.title("⚡ Shahrukh Algo - Nifty 750 Live Signals (Demo)")
    st.caption("नीचे दी गई टेबल में स्टॉक्स (₹50 से ₹900) के डेमो सिग्नल्स दिख रहे हैं। 'Open Chart 📈' पर क्लिक करके चेक करें।")

    # ₹50 से ₹900 की रेंज वाले डेमो स्टॉक्स का डेटा
    demo_signals = [
        {
            "Stock Symbol": "SUZLON",
            "LTP (₹)": 62.50,
            "Signal": "BUY",
            "15-Min High": 61.20,
            "Stop Loss": 59.80,
            "Risk/Trade": "₹ 1000",
            "Qty": 370,
            "TradingView Link": "https://in.tradingview.com/chart/?symbol=NSE:SUZLON"
        },
        {
            "Stock Symbol": "NHPC",
            "LTP (₹)": 94.10,
            "Signal": "BUY",
            "15-Min High": 92.50,
            "Stop Loss": 90.20,
            "Risk/Trade": "₹ 1000",
            "Qty": 260,
            "TradingView Link": "https://in.tradingview.com/chart/?symbol=NSE:NHPC"
        },
        {
            "Stock Symbol": "IRFC",
            "LTP (₹)": 152.30,
            "Signal": "BUY",
            "15-Min High": 149.80,
            "Stop Loss": 145.00,
            "Risk/Trade": "₹ 1000",
            "Qty": 138,
            "TradingView Link": "https://in.tradingview.com/chart/?symbol=NSE:IRFC"
        },
        {
            "Stock Symbol": "TATAMOTORS",
            "LTP (₹)": 875.00,
            "Signal": "BUY",
            "15-Min High": 862.00,
            "Stop Loss": 845.00,
            "Risk/Trade": "₹ 1000",
            "Qty": 58,
            "TradingView Link": "https://in.tradingview.com/chart/?symbol=NSE:TATAMOTORS"
        }
    ]

    df = pd.DataFrame(demo_signals)

    # Clickable Table Configuration
    st.dataframe(
        df,
        column_config={
            "TradingView Link": st.column_config.LinkColumn(
                "Direct Chart Link",
                help="Click to open stock chart in TradingView",
                display_text="Open Chart 📈"
            )
        },
        hide_index=True,
        use_container_width=True
    )
