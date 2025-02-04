import streamlit as st
import pandas as pd
import requests
import plotly.express as px

API_KEY = "NOHOAPQDZFQUZCO3"
BASE_URL = "https://www.alphavantage.co/query"

# Function to fetch stock data
def get_stock_data(ticker):
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "apikey": API_KEY,
        "outputsize": "compact"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if "Time Series (Daily)" in data:
        df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        return df
    else:
        return None

# Function to filter stocks based on criteria
def filter_stocks(pe_min, pe_max, industry, eps_min, growth_min):
    # Placeholder for actual stock screening logic
    stocks = pd.DataFrame({
        "Ticker": ["AAPL", "MSFT", "GOOGL"],
        "P/E Ratio": [28, 35, 30],
        "Industry": ["Tech", "Tech", "Tech"],
        "EPS": [5.5, 7.2, 6.8],
        "Growth Rate": [10, 12, 15]
    })
    
    filtered_stocks = stocks[(stocks["P/E Ratio"] >= pe_min) & (stocks["P/E Ratio"] <= pe_max) &
                              (stocks["EPS"] >= eps_min) & (stocks["Growth Rate"] >= growth_min)]
    
    if industry != "All":
        filtered_stocks = filtered_stocks[filtered_stocks["Industry"] == industry]
    
    return filtered_stocks

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
    st.write("### Filtered Stocks")
    st.dataframe(results)

# Stock Price Chart
st.header("Stock Price Performance")
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")
if st.button("Show Performance"):
    data = get_stock_data(ticker)
    if data is not None:
        fig = px.line(data, x=data.index, y="5. adjusted close", title=f"{ticker} Price Performance")
        st.plotly_chart(fig)
    else:
        st.error("Failed to retrieve stock data. Please check the ticker symbol or try again later.")

