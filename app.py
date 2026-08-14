import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import ta
from streamlit_autorefresh import st_autorefresh


# Fetching stock data based on the ticker, period, and interval
@st.cache_data(ttl=60)
def fetch_stock_data(ticker, period, interval):

    ticker = ticker.strip().upper()

    if not ticker:
        return pd.DataFrame()

    try:

        if period == "1wk":

            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=False,
                progress=False
            )

        else:

            data = yf.download(
                ticker,
                period=period,
                interval=interval,
                auto_adjust=False,
                progress=False
            )

        return data

    except Exception as e:

        st.error(f"Unable to fetch data for {ticker}: {e}")

        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_usd_inr_rate():

    try:
        data = yf.download(
            "USDINR=X",
            period="1d",
            interval="1m",
            auto_adjust=False,
            progress=False
        )

        if data.empty:
            return None

        if isinstance(data.columns, pd.MultiIndex):

            level_0 = data.columns.get_level_values(0)
            level_1 = data.columns.get_level_values(1)

            if "Close" in level_0:
                close_data = data["Close"]

            elif "Close" in level_1:
                close_data = data.xs(
                    "Close",
                    axis=1,
                    level=1
                )

            else:
                return None

            if isinstance(close_data, pd.DataFrame):
                close_data = close_data.iloc[:, 0]

        else:
            close_data = data["Close"]

        close_data = close_data.dropna()

        if close_data.empty:
            return None

        return float(close_data.iloc[-1])

    except Exception as e:

        st.warning(
            f"Unable to fetch USD/INR exchange rate: {e}"
        )

        return None


def convert_currency(
    value,
    from_currency,
    to_currency,
    exchange_rate
):

    if from_currency == to_currency:
        return value

    if exchange_rate is None:
        return None

    if from_currency == "USD" and to_currency == "INR":
        return value * exchange_rate

    if from_currency == "INR" and to_currency == "USD":
        return value / exchange_rate

    return value

def process_data(data):

    if data.empty:
        return data

    # Handle MultiIndex columns
    if isinstance(data.columns, pd.MultiIndex):

        if data.columns.nlevels == 2:

            level_0 = data.columns.get_level_values(0)
            level_1 = data.columns.get_level_values(1)

            # Case 1:
            # ('Open', 'AAPL'), ('High', 'AAPL'), ...
            if "Open" in level_0 or "Close" in level_0:
                data.columns = level_0

            # Case 2:
            # ('AAPL', 'Open'), ('AAPL', 'High'), ...
            elif "Open" in level_1 or "Close" in level_1:
                data.columns = level_1

            else:
                # Fallback
                data.columns = [
                    col[-1] for col in data.columns
                ]

    # Ensure DatetimeIndex
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)

    # Handle timezone
    if data.index.tz is None:
        data.index = data.index.tz_localize("UTC")

    data.index = data.index.tz_convert("US/Eastern")

    # Reset index
    data = data.reset_index()

    # Standardize datetime column
    if "Date" in data.columns:
        data.rename(
            columns={"Date": "Datetime"},
            inplace=True
        )

    elif "Datetime" not in data.columns:
        data.rename(
            columns={data.columns[0]: "Datetime"},
            inplace=True
        )

    return data

# Calculating basic metrics from the stock data
def calculate_metrics(data):

    if data.empty:
        return None

    # Latest available closing price
    last_close = float(data["Close"].iloc[-1])

    # Previous available closing price
    if len(data) > 1:
        previous_close = float(data["Close"].iloc[-2])
    else:
        previous_close = last_close

    # Daily price change
    change = last_close - previous_close

    if previous_close != 0:
        pct_change = (change / previous_close) * 100
    else:
        pct_change = 0.0

    # High and low over selected period
    period_high = float(data["High"].max())
    period_low = float(data["Low"].min())

    # Latest available volume
    latest_volume = int(data["Volume"].iloc[-1])

    return (
        last_close,
        change,
        pct_change,
        period_high,
        period_low,
        latest_volume
    )

# Adding simple moving average (SMA) and exponential moving average (EMA) indicators
def add_technical_indicators(data):

    data["SMA_20"] = ta.trend.sma_indicator(
        data["Close"],
        window=20
    )

    data["EMA_20"] = ta.trend.ema_indicator(
        data["Close"],
        window=20
    )

    data["RSI_14"] = ta.momentum.rsi(
        data["Close"],
        window=14
    )

    return data

def get_stock_currency(ticker):

    ticker = ticker.upper().strip()

    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        return "INR"

    return "USD"

def get_watchlist_data(
    watchlist,
    display_currency,
    usd_inr_rate
):

    results = []

    for symbol in watchlist:

        data = fetch_stock_data(
            symbol,
            "1d",
            "1m"
        )

        if data.empty:
            continue

        data = process_data(data)

        if data.empty or "Close" not in data.columns:
            continue

        last_price = float(
            data["Close"].iloc[-1]
        )

        opening_price = float(
            data["Open"].iloc[0]
        )

        if opening_price != 0:
            change_pct = (
                (last_price - opening_price)
                / opening_price
            ) * 100
        else:
            change_pct = 0.0

        # Determine native currency
        native_currency = get_stock_currency(symbol)

        # Convert price to selected currency
        display_price = convert_currency(
            last_price,
            native_currency,
            display_currency,
            usd_inr_rate
        )

        results.append({
            "Symbol": symbol,
            "Price": display_price,
            "Change %": change_pct
        })

    return pd.DataFrame(results)

# Creating the Dashboard App layout ##
# Set up Streamlit page layout
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# Minimal custom styling
st.markdown(
    """
    <style>
        .dashboard-header {
            padding: 0.5rem 0 1.2rem 0;
        }

        .dashboard-header h1 {
            margin-bottom: 0.2rem;
            font-size: 2.2rem;
        }

        .dashboard-header p {
            color: #888888;
            font-size: 1rem;
            margin-top: 0;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="dashboard-header">
        <h1>Stock Market Dashboard</h1>
        <p>Real-time market data and technical analysis</p>
    </div>
    """,
    unsafe_allow_html=True
)

# SIDEBAR PARAMETERS ############

# Sidebar for user input parameters
st.sidebar.header('Dashboard Controls')
ticker = st.sidebar.text_input(
    "Ticker",
    "AAPL"
)

time_period = st.sidebar.selectbox(
    "Time Period",
    ["1d", "1wk", "1mo", "1y", "max"]
)

chart_type = st.sidebar.selectbox(
    "Chart Type",
    ["Candlestick", "Line"]
)

currency = st.sidebar.selectbox(
    "Currency",
    ["USD", "INR"]
)

indicators = st.sidebar.multiselect(
    "Technical Indicators",
    ["SMA 20", "EMA 20", "RSI 14"]
)

st.sidebar.divider()
st.sidebar.header("Watchlist")

watchlist_input = st.sidebar.text_area(
    "Enter tickers",
    value="AAPL, MSFT, GOOGL, RELIANCE.NS, TCS.NS",
    help="Separate stock symbols with commas."
)

watchlist = [
    symbol.strip().upper()
    for symbol in watchlist_input.replace("\n", ",").split(",")
    if symbol.strip()
]

# Mapping of time periods to data intervals
interval_mapping = {
    '1d': '1m',
    '1wk': '30m',
    '1mo': '1d',
    '1y': '1wk',
    'max': '1wk'
}

# ==============================
# MAIN DASHBOARD
# ==============================

if st.sidebar.button("Update"):
    st.session_state["dashboard_loaded"] = True
if st.session_state.get("dashboard_loaded", False):

    # Fetch stock data

    data = fetch_stock_data(
        ticker,
        time_period,
        interval_mapping[time_period]
    )

    if data.empty:
        st.error(
            f"No market data found for '{ticker}'. "
            "Please check the ticker symbol."
        )
        st.stop()

    # Process data

    data = process_data(data)

    if data.empty:
        st.error("Unable to process stock data.")
        st.stop()

    # Add technical indicators

    data = add_technical_indicators(data)

    # Calculate metrics

    metrics = calculate_metrics(data)

    if metrics is None:
        st.error("Unable to calculate stock metrics.")
        st.stop()

    (
        last_close,
        change,
        pct_change,
        high,
        low,
        volume
    ) = metrics

    # Currency handling

    native_currency = get_stock_currency(ticker)

    usd_inr_rate = get_usd_inr_rate()

    display_last_close = convert_currency(
        last_close,
        native_currency,
        currency,
        usd_inr_rate
    )

    display_change = convert_currency(
        change,
        native_currency,
        currency,
        usd_inr_rate
    )

    display_high = convert_currency(
        high,
        native_currency,
        currency,
        usd_inr_rate
    )

    display_low = convert_currency(
        low,
        native_currency,
        currency,
        usd_inr_rate
    )

    # Currency symbol

    currency_symbol = {
        "USD": "$",
        "INR": "₹"
    }[currency]

    # Create currency-aware chart data

    chart_data = data.copy()

    for column in ["Open", "High", "Low", "Close"]:

        chart_data[column] = chart_data[column].apply(
            lambda value: convert_currency(
                value,
                native_currency,
                currency,
                usd_inr_rate
            )
        )

    # Convert technical indicators
    chart_data["SMA_20"] = chart_data["SMA_20"].apply(
        lambda value: convert_currency(
            value,
            native_currency,
            currency,
            usd_inr_rate
        ) if pd.notna(value) else value
    )

    chart_data["EMA_20"] = chart_data["EMA_20"].apply(
        lambda value: convert_currency(
            value,
            native_currency,
            currency,
            usd_inr_rate
        ) if pd.notna(value) else value
    )

    # Main metrics

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        label=f"{ticker} Price",
        value=f"{currency_symbol}{display_last_close:,.2f}",
        delta=f"{pct_change:.2f}%"
    )

    col2.metric(
        label="Period High",
        value=f"{currency_symbol}{display_high:,.2f}"
    )

    col3.metric(
        label="Period Low",
        value=f"{currency_symbol}{display_low:,.2f}"
    )

    col4.metric(
        label="Latest Volume",
        value=f"{volume:,}"
    )

    # Price chart

    fig = go.Figure()

    if chart_type == "Candlestick":

        fig.add_trace(
            go.Candlestick(
                x=chart_data["Datetime"],
                open=chart_data["Open"],
                high=chart_data["High"],
                low=chart_data["Low"],
                close=chart_data["Close"],
                name=ticker
            )
        )

    else:

        fig.add_trace(
            go.Scatter(
                x=chart_data["Datetime"],
                y=chart_data["Close"],
                mode="lines",
                name=ticker
            )
        )

    # Technical indicators

    for indicator in indicators:
        if indicator == "RSI 14":
            continue  # RSI will be plotted in a separate chart

        if indicator == "SMA 20":

            fig.add_trace(
                go.Scatter(
                    x=chart_data["Datetime"],
                    y=chart_data["SMA_20"],
                    mode="lines",
                    name="SMA 20"
                )
            )

        elif indicator == "EMA 20":

            fig.add_trace(
                go.Scatter(
                    x=chart_data["Datetime"],
                    y=chart_data["EMA_20"],
                    mode="lines",
                    name="EMA 20"
                )
            )

    # Format chart

    fig.update_layout(
        title=f"{ticker} — {time_period.upper()}",
        xaxis_title="Time",
        yaxis_title=f"Price ({currency})",
        height=600,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # RSI chart

    if "RSI 14" in indicators:

        rsi_fig = go.Figure()

        rsi_fig.add_trace(
            go.Scatter(
                x=chart_data["Datetime"],
                y=chart_data["RSI_14"],
                mode="lines",
                name="RSI 14"
            )
        )

        # Overbought level
        rsi_fig.add_hline(
            y=70,
            line_dash="dash",
            annotation_text="Overbought (70)"
        )

        # Oversold level
        rsi_fig.add_hline(
            y=30,
            line_dash="dash",
            annotation_text="Oversold (30)"
        )

        rsi_fig.update_layout(
            title="Relative Strength Index (RSI 14)",
            xaxis_title="Time",
            yaxis_title="RSI",
            height=300,
            yaxis=dict(
                range=[0, 100]
            ),
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(
            rsi_fig,
            use_container_width=True
        )

    # Historical data
    st.subheader("Historical Data")

    historical_data = chart_data[
        [
            "Datetime",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]
    ].copy()

    st.dataframe(
        historical_data,
        use_container_width=True
    )

    # Technical indicators table

    st.subheader("Technical Indicators")

    indicator_data = chart_data[
        [
            "Datetime",
            "SMA_20",
            "EMA_20",
            "RSI_14"
        ]
    ].copy()

    st.dataframe(
        indicator_data,
        use_container_width=True
    )

# ==============================
# WATCHLIST
# ==============================

if watchlist:

    st.subheader("Watchlist")

    watchlist_data = get_watchlist_data(
        watchlist,
        currency,
        get_usd_inr_rate()
    )

    if not watchlist_data.empty:

        currency_symbol = {
            "USD": "$",
            "INR": "₹"
        }[currency]

        watchlist_data["Price"] = watchlist_data[
            "Price"
        ].apply(
            lambda value: (
                f"{currency_symbol}{value:,.2f}"
            )
        )

        watchlist_data["Change %"] = watchlist_data[
            "Change %"
        ].apply(
            lambda value: f"{value:+.2f}%"
        )

        st.dataframe(
            watchlist_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No valid stock data found for the watchlist."
        )

auto_refresh = st.sidebar.checkbox(
    "Auto Refresh",
    value=False
)

if auto_refresh:

    refresh_interval = st.sidebar.selectbox(
        "Refresh Interval",
        [30, 60, 120, 300],
        index=1,
        format_func=lambda seconds: f"{seconds} seconds"
    )

    st_autorefresh(
        interval=refresh_interval * 1000,
        key="stock_dashboard_refresh"
    )

# Sidebar information section
st.sidebar.subheader('About')
st.sidebar.info('This dashboard provides stock data and technical indicators for various time periods. Use the sidebar to customize your view.')
