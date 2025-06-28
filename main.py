import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objects as go
from datetime import datetime
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh

API_KEY = st.secrets["API_KEY"]
TICKER_DURATION = 10



# ===== FETCHING CRYPTO DATA =====
if 'selected_crypto' not in st.session_state:
    st.session_state['selected_crypto'] = 'BTC-USD'
if 'crypto_symbol' not in st.session_state:
    st.session_state['crypto_symbol'] = st.session_state['selected_crypto'].split('-')[0]
if 'selected_interval' not in st.session_state:
    st.session_state['selected_interval'] = 'Days'
if 'selected_range' not in st.session_state:
    st.session_state['selected_range'] = 30
if 'selected_chart' not in st.session_state:
    st.session_state['selected_chart'] = 'Candlestick'
if 'show_volume' not in st.session_state:
    st.session_state['show_volume'] = 'Volume'
if 'selected_indicator' not in st.session_state:
    st.session_state['selected_indicator'] = None
if 'ticker_close' not in st.session_state:
    st.session_state['ticker_close'] = 0
if 'ticker_dataframe' not in st.session_state:
    st.session_state['ticker_dataframe'] = pd.DataFrame()
if 'ticker_ath_ts' not in st.session_state:
    st.session_state['ticker_ath_ts'] = "ath timestamp"

st.sidebar.title("⚙️ Configurations")
col1, col2, col3 = st.sidebar.columns(3)
col4, col5, col6 = st.sidebar.columns([2,1,3])

crypto_options = ["BTC-USD", "ETH-USD", 'XRP-USD', 
                  "BNB-USD", "SOL-USD", "TRX-USD", 
                  "DOGE-USD", "ADA-USD", "BCH-USD", 
                  "SUI-USD", "LINK-USD", "LTC-USD", 
                  "MATIC-USD", "DOT-USD", "AVAX-USD", 
                  "XLM-USD", "ETC-USD", "FIL-USD", 
                  "VET-USD", "ICP-USD", "ALGO-USD", 
                  "AAVE-USD", "UNI-USD", "XMR-USD",
                  "POL-USD"]
interval_options = ["Days", "Hours", "Minutes"]
range_options = [15, 30, 60, 90, 180]
indicator_options = ["MA", "EMA"]
chart_options = ["Candlestick", "Line", 'OHLC']
volume_options = ["Volume"]

with col1:
    st.session_state['selected_crypto'] = st.selectbox("🪙 Crypto", crypto_options)
with col2:
    st.session_state['selected_interval'] = st.selectbox("🕒 Interval", interval_options)
with col3:
    st.session_state['selected_range'] = st.selectbox("📆 Range", range_options, index=1)
with col4:
    st.session_state['selected_chart'] = st.selectbox("📈 Chart Type", chart_options)
with col5:
    st.session_state['show_volume'] = st.pills("", volume_options, selection_mode="single", default='Volume')
with col6:
    st.session_state['selected_indicator'] = st.pills("", indicator_options, selection_mode="single", default=None, disabled=st.session_state['selected_chart']=="Line")
st.session_state['crypto_symbol'] = st.session_state['selected_crypto'].split('-')[0]

@st.fragment(run_every=TICKER_DURATION)
def ticker_component():
    ticker_response = requests.get(
        f'https://data-api.coindesk.com/index/cc/v1/latest/tick',
        params={
            "market": "cadli",
            "instruments": {st.session_state['selected_crypto']},
            "apply_mapping": "true",
            "response_format": "JSON",
            "api_key": API_KEY
        },
        headers={"Content-type": "application/json; charset=UTF-8"}
    )
    ticker_data = ticker_response.json()
    df_ticker = pd.DataFrame.from_dict(ticker_data['Data'], orient='index').reset_index(drop=True)
    ticker_value = df_ticker['VALUE'].iloc[0]
    ticker_ath = df_ticker['LIFETIME_HIGH'].iloc[0]
    from_ath_change = ((ticker_value - ticker_ath) / ticker_ath) * 100
    st.session_state['ticker_dataframe'] = df_ticker
    st.session_state['ticker_close'] = ticker_value

    def number_format(value):
        if value >= 1:
            return f"{value:,.2f}"
        else:
            s = f"{value}"
            decimal = s.split(".")[1]
            count = 0
            for ch in decimal:
                if ch == '0':
                    count += 1
                else:
                    break
            return f"{value:.{count+4}f}"

    ticker_value = number_format(ticker_value)

    day_change = df_ticker['CURRENT_DAY_CHANGE_PERCENTAGE'].iloc[0]
    week_change = df_ticker['CURRENT_WEEK_CHANGE_PERCENTAGE'].iloc[0] 
    month_change = df_ticker['CURRENT_MONTH_CHANGE_PERCENTAGE'].iloc[0]
    year_change = df_ticker['CURRENT_YEAR_CHANGE_PERCENTAGE'].iloc[0]
    day_change = f"{day_change:.2f}%"
    week_change = f"{week_change:.2f}%"
    month_change = f"{month_change:.2f}%"
    year_change = f"{year_change:.2f}%"
    from_ath_change = f"{from_ath_change:.2f}%"
    day_high = f'${number_format(df_ticker['CURRENT_DAY_HIGH'].iloc[0])}'
    day_low = f'${number_format(df_ticker['CURRENT_DAY_LOW'].iloc[0])}'
    ticker_ath = number_format(ticker_ath)
    ticker_ath_ts = df_ticker['LIFETIME_HIGH_TS'].iloc[0]
    ticker_ath_ts = datetime.fromtimestamp(ticker_ath_ts)
    ticker_ath_ts = ticker_ath_ts.strftime('%d %b %Y')

    col1, col2, col3 = st.columns(3, vertical_alignment='center')
    with col1:
        st.metric(label=st.session_state['crypto_symbol'], value=f"${ticker_value}", delta=f"{day_change} (24h)")
    with col2:
        st.metric(label=f"ATH ({ticker_ath_ts})", value=f'${ticker_ath}')
    with col3:
        st.markdown(f'''H: :green-background[{day_high}]''')
        st.markdown(f'''L: :red-background[{day_low}]''')


    col4, col5, col6, col7 = st.columns(4)
    with col4:
        st.metric(label="1 week", value="", delta=week_change)
    with col5:
        st.metric(label="1 month", value="", delta=month_change)
    with col6:
        st.metric(label="1 year", value="", delta=year_change)
    with col7:
        st.metric(label="From ATH", value="", delta=from_ath_change)

ticker_component()


@st.fragment(run_every=60)
def chart_component():
    response = requests.get(
        f'https://data-api.coindesk.com/index/cc/v1/historical/{st.session_state['selected_interval'].lower()}',
        params={
            "market": "cadli",
            "instrument": st.session_state['selected_crypto'],
            "limit": 300,
            "aggregate": 1,
            "fill": "true",
            "apply_mapping": "true",
            "response_format": "JSON",
            "api_key": API_KEY
        },
        headers={"Content-type": "application/json; charset=UTF-8"}
    )
    data = response.json()
    df = pd.DataFrame(data['Data'])

    df.loc[df.index[-1], 'CLOSE'] = st.session_state['ticker_close']
    if df['HIGH'].iloc[-1] < st.session_state['ticker_close']:
        df.loc[df.index[-1], 'HIGH'] = st.session_state['ticker_close']
    if df['LOW'].iloc[-1] > st.session_state['ticker_close']:
        df.loc[df.index[-1], 'LOW'] = st.session_state['ticker_close']

    df['UTCTIME'] = pd.to_datetime(df['TIMESTAMP'].astype(int), unit='s')
    df['MA7'] = df['CLOSE'].rolling(window=7).mean()
    df['MA50'] = df['CLOSE'].rolling(window=50).mean()
    df['MA100'] = df['CLOSE'].rolling(window=100).mean()
    df['EMA7'] = df['CLOSE'].ewm(span=7, adjust=False).mean()
    df['EMA50'] = df['CLOSE'].ewm(span=50, adjust=False).mean()
    df['EMA100'] = df['CLOSE'].ewm(span=100, adjust=False).mean()

    show_range = st.session_state['selected_range']
    df_show = df.tail(show_range)
    df_show['VOLUME_COLOR'] = df_show.apply(
        lambda row: 'green' if row['CLOSE'] > row['OPEN'] else 'red', axis=1
    )

    if st.session_state['show_volume']!=None:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.00,
            row_heights=[0.85, 0.15],
            subplot_titles=(f"{st.session_state['selected_crypto']}", '')
        )
    else:
        fig = make_subplots(
            rows=1, cols=1,
            shared_xaxes=True,
            subplot_titles=(st.session_state['selected_crypto'],)
        )

    if st.session_state['selected_chart'] == "Candlestick":
        fig.add_trace(
            go.Candlestick(
                x=df_show['UTCTIME'],
                open=df_show['OPEN'],
                high=df_show['HIGH'],
                low=df_show['LOW'],
                close=df_show['CLOSE'],
                name='Candlestick',
                showlegend=False
            ),
            row=1, col=1
        )
    elif st.session_state['selected_chart'] == "Line":
        fig.add_trace(
            go.Scatter(
                x=df_show['UTCTIME'],
                y=df_show['CLOSE'],
                mode='lines+markers',
                name='Close Price',
                line=dict(width=1.5),
                marker=dict(size=4),
                showlegend=False
            ),
            row=1, col=1
        )
    elif st.session_state['selected_chart'] == "OHLC":
        fig.add_trace(
            go.Ohlc(
                x=df_show['UTCTIME'],
                open=df_show['OPEN'],
                high=df_show['HIGH'],
                low=df_show['LOW'],
                close=df_show['CLOSE'],
                name='OHLC',
                showlegend=False
            ),
            row=1, col=1
        )

    if st.session_state['show_volume']!=None:
        fig.add_trace(
            go.Bar(
                x=df_show['UTCTIME'],
                y=df_show['VOLUME'],
                name=f'Volume ({st.session_state['crypto_symbol']})',
                marker_color=df_show['VOLUME_COLOR'],
                marker_opacity=0.25,
                showlegend=False
            ),
            row=2, col=1
        )

    if st.session_state['selected_chart'] == "Candlestick" or st.session_state['selected_chart'] == "OHLC":
        if st.session_state['selected_indicator'] == "MA":
            fig.add_trace(go.Scatter(
                x=df_show['UTCTIME'],
                y=df_show['MA7'],
                mode='lines',
                name='MA(7)',
                line=dict(color='orange', width=1.5)
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df_show['UTCTIME'],
                y=df_show['MA50'],
                mode='lines',
                name='MA(50)',
                line=dict(color='cyan', width=1.5)
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df_show['UTCTIME'],
                y=df_show['MA100'],
                mode='lines',
                name='MA(100)',
                line=dict(color='purple', width=1.5)
            ), row=1, col=1)
        elif st.session_state['selected_indicator'] == "EMA":
            fig.add_trace(go.Scatter(
                x=df_show['UTCTIME'],
                y=df_show['EMA7'],
                mode='lines',
                name='EMA(7)',
                line=dict(color='orange', width=1.5)
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df_show['UTCTIME'],
                y=df_show['EMA50'],
                mode='lines',
                name='EMA(50)',
                line=dict(color='cyan', width=1.5)
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df_show['UTCTIME'],
                y=df_show['EMA100'],
                mode='lines',
                name='EMA(100)',
                line=dict(color='purple', width=1.5)
            ), row=1, col=1)

    fig.update_layout(
        template='plotly_dark',
        dragmode=False,
        showlegend=True,
        xaxis_rangeslider_visible=False,
    )

    if st.session_state['show_volume']!=None:
        fig.update_xaxes(showgrid=True, row=1, col=1)
        fig.update_xaxes(showgrid=True, row=2, col=1)
        fig.update_yaxes(showgrid=False, row=2, col=1)
        fig.update_yaxes(showticklabels=False, row=2, col=1)
    else:
        fig.update_xaxes(showgrid=True, row=1, col=1)

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.metric(label="All Time High", value='$109,030.12')
chart_component()
# === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === ===


# ===== FEAR & GREED INDEX =====
with st.sidebar:
    @st.fragment(run_every=TICKER_DURATION)
    def fng_index():
        st.divider()
        st.title("😯 Crypto Market Sentiment")
        
        fng_url = "https://api.alternative.me/fng/?limit=30&format=json"
        fng_response = requests.get(fng_url)
        fng_data = fng_response.json()['data']

        df_fng = pd.DataFrame(fng_data)
        df_fng.rename(
            columns={
                'value': 'FNG_VALUE',
                'value_classification': 'FNG_CLASS'
            }, 
            inplace=True)
        df_fng['FNG_VALUE'] = pd.to_numeric(df_fng['FNG_VALUE'])
        df_fng['UTCTIME'] = pd.to_datetime(df_fng['timestamp'].astype(int), unit='s')
        df_fng = df_fng.sort_values(by='UTCTIME').reset_index(drop=True)

        latest_fng = df_fng.iloc[-1]
        yesterday_fng = int(df_fng.iloc[-2]['FNG_VALUE'])
        fng_value =  latest_fng['FNG_VALUE']
        fng_class =  latest_fng['FNG_CLASS']
        if fng_class == "Extreme Fear":
            st.markdown(f":red-badge[📊 Fear & Greed Index: **{fng_value}/100**] :red-badge[😱 Crypto market is in **EXTREME FEAR**]")
        elif fng_class == "Fear":
            st.markdown(f":red-badge[📊 Fear & Greed Index: **{fng_value}/100**] :red-badge[😟 Crypto market is in **FEAR**]")
        elif fng_class == "Neutral":
            st.markdown(f":orange-badge[📊 Fear & Greed Index: **{fng_value}/100**] :orange-badge[😐 Crypto market is **NEUTRAL**]") 
        elif fng_class == "Greed":
            st.markdown(f":green-badge[📊 Fear & Greed Index: **{fng_value}/100**] :green-badge[🙂 Crypto market is in **GREED**]")
        else:
            st.markdown(f":green-badge[📊 Fear & Greed Index: **{fng_value}/100**] :green-badge[😎 Crypto market is in EXTREME **GREED**]")

        df_fng_chart = df_fng.tail(30)
        df_fng_chart = df_fng_chart.set_index('UTCTIME')
        fng_line_data = df_fng_chart[['FNG_VALUE']]
        st.line_chart(fng_line_data, y_label='F&G Index Value', height=200)

    fng_index()
# === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === ===
