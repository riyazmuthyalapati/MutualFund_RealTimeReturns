import streamlit as st
import requests
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime
from google import genai
import os

# Set page config
st.set_page_config(
    page_title="Motilal Midcap Fund Real time returns",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Gemini API key from Streamlit Cloud secrets
api_key = st.secrets["api_key"]
client = genai.Client(api_key=api_key)

# Custom CSS for mobile responsiveness
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    [data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
    }
    .stButton > button {
        width: 100%;
        margin: 0.25rem 0;
    }
    .streamlit-expanderHeader { font-size: 0.9rem; }
    .dataframe { font-size: 0.8rem; }
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1.1rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for stock data
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = {
        "DIXON": {"url": "https://www.screener.in/company/DIXON/consolidated/", "allocation": 10.08},
        "COFORGE": {"url": "https://www.screener.in/company/COFORGE/consolidated/", "allocation": 9.79},
        "TRENT": {"url": "https://www.screener.in/company/TRENT/consolidated/", "allocation": 9.14},
        "ETERNAL": {"url": "https://www.screener.in/company/ETERNAL/consolidated/", "allocation": 9.03},
        "KALYANKJIL": {"url": "https://www.screener.in/company/KALYANKJIL/consolidated/", "allocation": 8.70},
        "PAYTM": {"url": "https://www.screener.in/company/PAYTM/consolidated/", "allocation": 8.68},
        "PERSISTENT": {"url": "https://www.screener.in/company/PERSISTENT/consolidated/", "allocation": 8.39},
        "POLYCAB": {"url": "https://www.screener.in/company/POLYCAB/consolidated/", "allocation": 6.22},
        "KEI": {"url": "https://www.screener.in/company/KEI/", "allocation": 4.11},
        "KAYNES": {"url": "https://www.screener.in/company/KAYNES/consolidated/", "allocation": 3.70},
        "BHARTIHEXA": {"url": "https://www.screener.in/company/BHARTIHEXA/", "allocation": 3.34},
        "MAXHEALTH": {"url": "https://www.screener.in/company/MAXHEALTH/consolidated/", "allocation": 3.21},
        "ABCAPITAL": {"url": "https://www.screener.in/company/ABCAPITAL/consolidated/", "allocation": 3.20},
        "TIINDIA": {"url": "https://www.screener.in/company/TIINDIA/consolidated/", "allocation": 2.98},
        "PRESTIGE": {"url": "https://www.screener.in/company/PRESTIGE/consolidated/", "allocation": 2.58},
        "SUPREMEIND": {"url": "https://www.screener.in/company/SUPREMEIND/consolidated/", "allocation": 2.38},
        "KPITTECH": {"url": "https://www.screener.in/company/KPITTECH/consolidated/", "allocation": 1.03},
        "POWERINDIA": {"url": "https://www.screener.in/company/POWERINDIA", "allocation": 0.86}
    }

# App title
st.title("📈 Portfolio Tracker")
st.markdown("*Real-time stock returns*")
st.markdown("*By - Riyaz M*")

@st.cache_data(ttl=300)
def fetch_stock_return(url, stock_name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        match = re.search(r"[+-]?[0-9]+\.[0-9]+(?=%)", soup.text)
        if match:
            return float(match.group())
        else:
            return 0.0
    except Exception as e:
        st.error(f"Error fetching {stock_name}: {str(e)}")
        return 0.0

def calculate_portfolio_return():
    portfolio_data = []
    total_allocation = sum(data["allocation"] for data in st.session_state.stock_data.values())
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_weighted_return = 0

    for i, (stock_name, data) in enumerate(st.session_state.stock_data.items()):
        status_text.text(f'Fetching {stock_name}...')
        stock_return = fetch_stock_return(data["url"], stock_name)
        normalized_allocation = data["allocation"] / total_allocation if total_allocation > 0 else 0
        weighted_return = stock_return * normalized_allocation
        total_weighted_return += weighted_return

        portfolio_data.append({
            "Stock": stock_name,
            "Return": f"{stock_return:+.2f}%",
            "Weight": f"{data['allocation']:.1f}%",
            "Contribution": f"{weighted_return:+.3f}%"
        })

        progress_bar.progress((i + 1) / len(st.session_state.stock_data))
        time.sleep(0.1)

    progress_bar.empty()
    status_text.empty()
    return portfolio_data, total_weighted_return

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Portfolio", "⚙️ Manage", "🤖 Ask AI"])

# ---------------- TAB 1: Portfolio ----------------
with tab1:
    st.button("🔄 Refresh Data", type="primary", use_container_width=True)
    st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    if len(st.session_state.stock_data) > 0:
        with st.spinner("Loading portfolio..."):
            portfolio_data, total_return = calculate_portfolio_return()

        st.metric("📈 Portfolio Return Today", f"{total_return:+.2f}%")
        col1, col2 = st.columns(2)
        with col1:
            positive_stocks = len([s for s in portfolio_data if float(s["Return"].replace('%', '').replace('+', '')) > 0])
            st.metric("Green Stocks", f"{positive_stocks}/{len(portfolio_data)}")
        with col2:
            total_allocation = sum(data["allocation"] for data in st.session_state.stock_data.values())
            st.metric("Total Weight", f"{total_allocation:.0f}%")

        st.markdown("---")
        st.subheader("📊 Stock Performance")
        df = pd.DataFrame(portfolio_data)

        def highlight_returns(val):
            if isinstance(val, str) and '%' in val:
                try:
                    numeric_val = float(val.replace('%', '').replace('+', ''))
                    if numeric_val > 0:
                        return 'background-color: #d4edda; color: #155724'
                    elif numeric_val < 0:
                        return 'background-color: #f8d7da; color: #721c24'
                except:
                    pass
            return ''

        styled_df = df.style.applymap(highlight_returns)
        st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)

        st.markdown("---")
        st.subheader("📈 Today's Highlights")
        best = max(portfolio_data, key=lambda x: float(x["Return"].replace('%', '').replace('+', '')))
        worst = min(portfolio_data, key=lambda x: float(x["Return"].replace('%', '').replace('+', '')))
        st.success(f"🏆 **Best**: {best['Stock']} ({best['Return']})")
        st.error(f"📉 **Worst**: {worst['Stock']} ({worst['Return']})")

    else:
        st.warning("📱 No stocks in portfolio. Add stocks in the 'Manage' tab.")

# ---------------- TAB 2: Manage ----------------
with tab2:
    st.subheader("⚙️ Portfolio Management")
    st.markdown("### ➕ Add Stock")

    new_stock_symbol = st.text_input("Stock Symbol", placeholder="e.g., RELIANCE", key="new_stock")
    new_stock_url = st.text_input("Screener URL", placeholder="https://www.screener.in/company/RELIANCE/", key="new_url")
    new_allocation = st.number_input("Weight %", min_value=0.01, max_value=100.0, value=1.0, step=0.1, key="new_allocation")

    if st.button("➕ Add to Portfolio", type="primary", use_container_width=True):
        if new_stock_symbol and new_stock_url:
            if new_stock_symbol.upper() not in st.session_state.stock_data:
                st.session_state.stock_data[new_stock_symbol.upper()] = {
                    "url": new_stock_url,
                    "allocation": new_allocation
                }
                # Auto-sort by weight
                st.session_state.stock_data = dict(sorted(
                    st.session_state.stock_data.items(),
                    key=lambda x: x[1]["allocation"],
                    reverse=True
                ))
                st.success(f"✅ Added {new_stock_symbol.upper()}!")
                st.rerun()
            else:
                st.error(f"❌ {new_stock_symbol.upper()} already exists!")
        else:
            st.error("❌ Please fill in both fields!")

    st.markdown("---")
    st.markdown("### ✏️ Edit Stocks")

    if len(st.session_state.stock_data) > 0:
        for stock, data in st.session_state.stock_data.items():
            with st.expander(f"📈 {stock} ({data['allocation']:.1f}%)"):
                new_url = st.text_input("URL", value=data['url'], key=f"url_{stock}")
                new_alloc = st.number_input("Weight %", min_value=0.01, max_value=100.0, 
                                          value=data['allocation'], step=0.1, key=f"alloc_{stock}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Update", key=f"update_{stock}", use_container_width=True):
                        st.session_state.stock_data[stock]['url'] = new_url
                        st.session_state.stock_data[stock]['allocation'] = new_alloc
                        # Auto-sort
                        st.session_state.stock_data = dict(sorted(
                            st.session_state.stock_data.items(),
                            key=lambda x: x[1]["allocation"],
                            reverse=True
                        ))
                        st.success(f"✅ Updated {stock}!")
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{stock}", use_container_width=True):
                        del st.session_state.stock_data[stock]
                        st.success(f"✅ Deleted {stock}!")
                        st.rerun()

        st.markdown("---")
        total_allocation = sum(data["allocation"] for data in st.session_state.stock_data.values())
        st.metric("Total Stocks", len(st.session_state.stock_data))
        st.metric("Total Weight", f"{total_allocation:.1f}%")
        if abs(total_allocation - 100) > 1:
            st.warning(f"⚠️ Total weight: {total_allocation:.1f}%. Consider adjusting to 100%.")
    else:
        st.info("📱 No stocks yet. Add your first stock above!")

# ---------------- TAB 3: AI Assistant ----------------
with tab3:
    st.subheader("🤖 Ask AI about your Portfolio")
    st.markdown("Ask questions like:")
    st.markdown("- Which stock gave the highest return?")
    st.markdown("- What is the total weighted return?")
    st.markdown("- Which stocks have negative returns?")

    if 'portfolio_data' not in locals():
        st.warning("Please refresh your portfolio first from the 📊 Portfolio tab.")
    else:
        user_question = st.text_input("💬 Your Question", placeholder="e.g., Which stock performed best today?")
        if st.button("Ask", type="primary", use_container_width=True):
            if user_question.strip():
                with st.spinner("Thinking... 🤔"):
                    table_text = "\n".join([
                        f"{row['Stock']}: Return {row['Return']}, Weight {row['Weight']}, Contribution {row['Contribution']}"
                        for row in portfolio_data
                    ])
                    prompt = f"""
                    You are a financial assistant. 
                    Below is today's portfolio performance data:
                    {table_text}

                    Based on this data, answer the following question clearly and concisely:
                    {user_question}
                    """
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt
                        )
                        st.success("✅ AI Response:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please type a question before clicking Ask.")

st.markdown("---")
st.caption("*Data from Screener.in • Updates every 5min • AI by Google Gemini*")
