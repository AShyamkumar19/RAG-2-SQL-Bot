import yfinance as yf
import pandas as pd

sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
table = pd.read_html(sp500_url)
sp500_ticker = table[0]['Symbol'].tolist()
print(sp500_ticker) 

def get_sp500_data(symbols, start_date, end_date):
    data = yf.download(symbols, start=start_date, end=end_date, grout_by='ticker')
    return data

sp500_data = get_sp500_data(sp500_ticker, '2020-01-01', '2023-12-31')

print(sp500_data.head())