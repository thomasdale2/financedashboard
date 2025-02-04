import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

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

# Function to filter stocks dynamically
def filter_stocks(pe_min, pe_max, industry, eps_min, growth_min, tickers):
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
tickers_input = st.sidebar.text_area("Enter Stock Tickers (comma-separated)", "")

if st.sidebar.button("Screen Stocks"):
    tickers = [ticker.strip() for ticker in tickers_input.split(",")]
    results = filter_stocks(pe_min, pe_max, industry, eps_min, growth_min, tickers)
    st.write("### Filtered Stocks")
    st.dataframe(results)

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
