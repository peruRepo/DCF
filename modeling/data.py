"""
Utilizing financialmodelingprep.com for their free-endpoint API
to gather company financials.

NOTE: Some code taken directly from their documentation. See: https://financialmodelingprep.com/developer/docs/. 
"""

from urllib.request import urlopen
import os
import json, traceback
import yfinance as yf
import requests
from pandas_datareader import data as pdr

# https://financialmodelingprep.com/api/v3/financials/income-statement/AAPL?apikey=
def get_api_url(requested_data, ticker, period, apikey):
    if period == 'annual':
        url = 'https://financialmodelingprep.com/api/v3/{requested_data}/{ticker}?apikey={apikey}'.format(
            requested_data=requested_data, ticker=ticker, apikey=apikey)
    elif period == 'quarter':
        url = 'https://financialmodelingprep.com/api/v3/{requested_data}/{ticker}?period=quarter&apikey={apikey}'.format(
            requested_data=requested_data, ticker=ticker, apikey=apikey)
    else:
        raise ValueError("invalid period " + str(period))
    return url


def get_jsonparsed_data(url,  ticker , requested_data,):
    """
    Fetch url, return parsed json. 

    args:
        url: the url to fetch.
    
    returns:
        parsed json
    """

    directory = ''
    if(not os.environ.get('cache_dir') == '' ):
        directory = os.environ.get('cache_dir')
    fileName = requested_data+'-'+ticker+'.json'


    if (not fileName.startswith('financials')):
        fileName = directory + 'financials/'+fileName
    else :
        fileName = directory + fileName



    if os.path.exists(fileName):
        with open(fileName) as f:
          json_data = json.load(f)
    else :
        try: response = urlopen(url)
        except Exception as e:
            print(f"Error retrieving {url}:")
            try: print("\t%s"%e.read().decode())
            except: pass
            raise
        data = response.read().decode('utf-8')
        json_data = json.loads(data)

        with open(fileName, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        if "Error Message" in json_data:
            raise ValueError("Error while requesting data from '{url}'. Error Message: '{err_msg}'.".format(
                url=url, err_msg=json_data["Error Message"]))
    return json_data


def get_EV_statement(ticker, period='annual', apikey=''):
    """
    Fetch EV statement, with details like total shares outstanding, from FMP.com

    args:
        ticker: company tickerr
    returns:
        parsed EV statement
    """
    url = get_api_url('enterprise-value', ticker=ticker, period=period, apikey=apikey)
    # with open('data/ev.json') as f:
    #     jsondata = json.load(f)
    jsondata = get_jsonparsed_data(url, ticker, 'enterprise-value')
    # with open('data/ev.json', 'w', encoding='utf-8') as f:
    #     json.dump(jsondata, f, ensure_ascii=False, indent=4)
    return jsondata


#! TODO: maybe combine these with argument flag for which statement, seems pretty redundant tbh
def get_income_statement(ticker, period='annual', apikey=''):
    """
    Fetch income statement.

    args:
        ticker: company ticker.
        period: annual default, can fetch quarterly if specified. 

    returns:
        parsed company's income statement
    """
    url = get_api_url('financials/income-statement', ticker=ticker, period=period, apikey=apikey)
    jsondata = get_jsonparsed_data(url,ticker,'financials/income-statement')
    # with open('data/income.json', 'w', encoding='utf-8') as f:
    #     json.dump(jsondata, f, ensure_ascii=False, indent=4)

    return jsondata


def get_cashflow_statement(ticker, period='annual', apikey=''):
    """
    Fetch cashflow statement.

    args:
        ticker: company ticker.
        period: annual default, can fetch quarterly if specified. 

    returns:
        parsed company's cashflow statement
    """
    url = get_api_url('financials/cash-flow-statement', ticker=ticker, period=period, apikey=apikey)
    # with open('data/cf.json') as f:
    #     jsondata = json.load(f)
    jsondata = get_jsonparsed_data(url, ticker,'financials/cash-flow-statement' )
    # with open('data/cf.json', 'w', encoding='utf-8') as f:
    #     json.dump(jsondata, f, ensure_ascii=False, indent=4)
    return jsondata


def get_balance_statement(ticker, period='annual', apikey=''):
    """
    Fetch balance sheet statement.

    args:
        ticker: company ticker.
        period: annual default, can fetch quarterly if specified. 

    returns:
        parsed company's balance sheet statement
    """

    url = get_api_url('financials/balance-sheet-statement', ticker=ticker, period=period, apikey=apikey)

    # with open(fileName) as f:
    #     jsondata = json.load(f)
    jsondata = get_jsonparsed_data(url, ticker , 'financials/balance-sheet-statement')
    # with open('data/balance.json', 'w', encoding='utf-8') as f:
    #     json.dump(jsondata, f, ensure_ascii=False, indent=4)
    return jsondata


def get_stock_price(ticker, apikey=''):
    """
    Fetches the stock price for a ticker

    args:
        ticker
    
    returns:
        {'symbol': ticker, 'price': price}
    """
    # url = 'https://financialmodelingprep.com/api/v3/stock/real-time-price/{ticker}?apikey={apikey}'.format(
    #     ticker=ticker, apikey=apikey)
    # yf.pdr_override()
    # stock_info = yf.Ticker(ticker).info
    # stock_info = pdr.get_data_yahoo(ticker,start="2023-01-25", end="2023-01-25")
    # cf = pdr.Ticker(ticker).cashflow
    # stock_info.keys() for other properties you can explore
    # r = requests.get(url="https://query1.finance.yahoo.com/v10/finance/quoteSummary/"+ticker+"?modules=financialData")
    # stock_info = r.json();

    # ticker = yf.Ticker(ticker)
    # hist  = ticker.history(period="1d")
    # df = hist.reset_index()
    # market_price = {}
    # for index, row in df.iterrows():
    #     market_price['price']  = row['Close']
    market_price = {}
    stock_info = yf.Ticker(ticker).fast_info
    market_price['price'] = stock_info['last_price']
    # market_price['price'] = float(0)
    return market_price


def get_batch_stock_prices(tickers, apikey=''):
    """
    Fetch the stock prices for a list of tickers.

    args:
        tickers: a list of  tickers........
    
    returns:
        dict of {'ticker':  price}
    """
     # prices = {'AAPL' : 137.87}
    prices = {}
    for ticker in tickers:
        prices[ticker] = get_stock_price(ticker=ticker, apikey=apikey)['price']

    return prices


def get_historical_share_prices(ticker, dates, apikey=''):
    """
    Fetch the stock price for a ticker at the dates listed.

    args:
        ticker: a ticker.
        dates: a list of dates from which to fetch close price.

    returns:
        {'date': price, ...}
    """
    prices = {}
    for date in dates:
        try: date_start, date_end = date[0:8] + str(int(date[8:]) - 2), date
        except:
            print(f"Error parsing '{date}' to date.")
            print(traceback.format_exc())
            continue
        # url = 'https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={date_start}&to={date_end}&apikey={apikey}'.format(
        #     ticker=ticker, date_start=date_start, date_end=date_end, apikey=apikey)
        prices = yf.download(ticker, start=date_start,
                           end=date_end)

        # try:
        #     prices[date_end] = get_jsonparsed_data(url, ticker, 'historical-price-full')['historical'][0]['close']
        #
        # except IndexError:
        #     #  RIP nested try catch, so many issues with dates just try a bunch and get within range of earnings release
        #     try:
        #         prices[date_start] = get_jsonparsed_data(url, ticker, 'historical-price-full')['historical'][0]['close']
        #     except IndexError:
        #         print(date + ' ', get_jsonparsed_data(url, ticker, 'historical-price-full'))

    return prices


if __name__ == '__main__':
    """ quick test, to use run data.py directly """

    ticker = 'AAPL'
    apikey = '<DEMO>'
    # data = get_cashflow_statement(ticker=ticker, apikey=apikey)
    # print(data)
