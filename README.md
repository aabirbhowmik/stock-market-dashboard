# 📈 Stock Market Dashboard

A real-time stock market dashboard built with **Python and Streamlit** for monitoring US and Indian stocks with interactive charts, technical indicators, currency conversion, watchlists, and automatic refresh.

## 🚀 Features

- Real-time stock market data using Yahoo Finance
- Support for US and Indian stocks
- Candlestick and line charts
- Multiple time periods
- USD ↔ INR currency conversion
- SMA 20
- EMA 20
- RSI 14
- Customizable watchlist
- Automatic data refresh
- Historical market data
- Interactive Plotly charts
- Error handling for invalid or unavailable tickers
- Clean and minimal user interface

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **yfinance**
- **Plotly**
- **TA**
- **streamlit-autorefresh**

## 📊 Supported Markets

### US Stocks

Examples:

```text
AAPL
MSFT
GOOGL
AMZN
NVDA
```

### Indian Stocks

Examples:
```
RELIANCE.NS
TCS.NS
INFY.NS
HDFCBANK.NS
```
The application automatically detects .NS and .BO ticker symbols as INR-denominated stocks.

### 📈 Technical Indicators
SMA 20

20-period Simple Moving Average used to identify short-term price trends.

EMA 20

20-period Exponential Moving Average that gives greater weight to recent prices.

RSI 14

14-period Relative Strength Index used to analyze price momentum.

Reference levels:

70 — Overbought
30 — Oversold

Technical indicators are provided for educational and analytical purposes and should not be considered financial advice.

## 💱 Currency Conversion

The dashboard supports:
```
USD
INR
```
Stock prices can be converted between USD and INR using the latest available USD/INR exchange rate retrieved through Yahoo Finance.

Currency conversion is applied to:
```
Stock price
Period high
Period low
Price charts
SMA 20
EMA 20
Watchlist prices
```
RSI and percentage changes are unaffected by currency conversion.

## ⭐ Watchlist

Users can monitor multiple stocks through a customizable watchlist.

Example:

AAPL, MSFT, GOOGL, RELIANCE.NS, TCS.NS

The watchlist displays:

Stock symbol
Current price
Percentage change

The watchlist supports both US and Indian stocks.

## 🔄 Auto Refresh

The dashboard supports optional automatic refresh with the following intervals:

30 seconds
60 seconds
120 seconds
300 seconds
##📁 Project Structure
```text
STOCK MARKET DASHBOARD/
│
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

### ⚙️ Installation
1. Clone the repository
```
git clone <your-github-repository-url>
cd STOCK-MARKET-DASHBOARD
```
2. Create a virtual environment
```
python -m venv .venv
```
4. Activate the virtual environment
```
Windows
.venv\Scripts\activate
macOS / Linux
source .venv/bin/activate
```
6. Install dependencies
```
pip install -r requirements.txt
```
8. Run the application
```
python -m streamlit run app.py
```
The application will be available at:

http://localhost:8501
## 🧭 Usage
Enter a stock ticker in the sidebar.
Select the desired time period.
Choose a chart type.
Select USD or INR.
Select technical indicators.
Click Update.
Add stocks to the watchlist.
Enable Auto Refresh when required.
Example — US Stock
Ticker: AAPL
Currency: USD
Chart Type: Candlestick
Indicators: SMA 20, EMA 20, RSI 14
Example — Indian Stock
Ticker: RELIANCE.NS
Currency: INR
Chart Type: Candlestick
Indicators: SMA 20, EMA 20, RSI 14
## 📡 Data Source

Market data is retrieved from Yahoo Finance using the yfinance Python library.

This project is intended for educational and portfolio purposes and should not be considered financial advice.

## 📄 License

This project is available for educational and portfolio purposes.

## 👨‍💻 Author
```
Aabir Bhowmik
```
