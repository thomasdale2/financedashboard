import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from yahooquery import Screener

# Function to fetch stock data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="6mo")
    if not df.empty:
        return df
    else:
        return None

# Function to fetch stock fundamentals
def get_stock_fundamentals(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return info if "symbol" in info else None

# Function to get a list of tickers from S&P 500
def get_sp500_tickers():
    s = Screener()
    data = s.get_screeners('all_usa', count=100)
    tickers = data['all_usa']['quotes']
    return [ticker['symbol'] for ticker in tickers]

# Function to filter stocks dynamically
def filter_stocks(pe_min, pe_max, industry, eps_min, growth_min):
    tickers = get_sp500_tickers()

    filtered_stocks = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if "trailingPE" in info and "trailingEps" in info and "sector" in info and "industry" in info:
            pe_ratio = info["trailingPE"]
            eps = info["trailingEps"]
            sector = info["sector"]
            industry_info = info["industry"]
            
            if (pe_min <= pe_ratio <= pe_max and
                eps >= eps_min and
                info.get("revenueGrowth", 0) * 100 >= growth_min and
                (industry == "All" or industry == industry_info)):

                filtered_stocks.append({
                    "Ticker": ticker,
                    "P/E Ratio": pe_ratio,
                    "Industry": industry_info,
                    "EPS": eps,
                    "Growth Rate (%)": info.get("revenueGrowth", 0) * 100
                })
    
    return pd.DataFrame(filtered_stocks)

# Streamlit UI
st.title("Stock Screener and Price Dashboard")

# Sidebar Filters
st.sidebar.header("Stock Screener")
pe_min = st.sidebar.number_input("Min P/E Ratio", value=10)
pe_max = st.sidebar.number_input("Max P/E Ratio", value=40)
industry = st.sidebar.selectbox("Industry", ["All", "Tech", "Healthcare", "Finance"])
eps_min = st.sidebar.number_input("Min EPS", value=0.0)
growth_min = st.sidebar.number_input("Min Growth Rate (%)", value=0.0)

if st.sidebar.button("Screen Stocks"):
    results = filter_stocks(pe_min, pe_max, industry, eps_min, growth_min)
    
    # Pagination
    page_size = 10
    total_rows = results.shape[0]
    total_pages = max(1, total_rows // page_size + (total_rows % page_size > 0))
    page_num = st.sidebar.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    start_row = (page_num - 1) * page_size
    end_row = start_row + page_size
    
    st.write("### Filtered Stocks")
    st.dataframe(results.iloc[start_row:end_row])

# Stock Price Chart
st.header("Stock Price Performance")
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")
if st.button("Show Performance"):
    data = get_stock_data(ticker)
    if data is not None:
        fig = px.line(data, x=data.index, y="Close", title=f"{ticker} Price Performance")
        st.plotly_chart(fig)
    else:
        st.error("Failed to retrieve stock data. Please check the ticker symbol or try again later.")

# Stock Fundamentals
st.header("Stock Fundamentals")
if st.button("Show Fundamentals"):
    fundamentals = get_stock_fundamentals(ticker)
    if fundamentals:
        st.write(f"### {fundamentals['longName']} ({fundamentals['symbol']})")
        st.write(f"- **Sector:** {fundamentals['sector']}")
        st.write(f"- **Industry:** {fundamentals['industry']}")
        st.write(f"- **P/E Ratio:** {fundamentals.get('trailingPE', 'N/A')}")
        st.write(f"- **EPS:** {fundamentals.get('trailingEps', 'N/A')}")
        st.write(f"- **Market Cap:** {fundamentals.get('marketCap', 'N/A')}")
    else:
        st.error("Failed to retrieve fundamentals. Please check the ticker symbol or try again later.")
