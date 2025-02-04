import yfinance as yf
import os
import json, traceback
from yahooquery import Ticker as yq

from utility.CommonUtil import isFloat


def get_stock_info_yf(ticker):
    return yq.Ticker(ticker)


def get_EV_statement_yf(ticker, balance_statement):
    """
    Fetch EV statement, with details like total shares outstanding, from FMP.com

    args:
        ticker: company tickerr
    returns:
        parsed EV statement
    """
    ticker_info = ticker.info
    total_debt = balance_statement[0]['Total Debt']
    cash_and_cash_equivalents = balance_statement[0]['Cash And Cash Equivalents']
    # ticker_info.get('totalCash')

        # ticker_info.get('totalDebt'))
    total_shares = ticker_info.get('sharesOutstanding')

    data = {
        'Cash & Cash Equivalents': cash_and_cash_equivalents,
        'Total Debt': total_debt,
        'Total Shares Outstanding': total_shares,
        '- Cash & Cash Equivalents': cash_and_cash_equivalents,
        '+ Total Debt': total_debt,
        'Number of Shares': total_shares
    }

    # Convert the dictionary to a DataFrame
    ev = []
    ev.append(data)
    return ev

def get_cashflow_statement_yf(ticker, period='annual', statementName='cashflow_statment', tickerName=''):
    # ticker = yf.Ticker(ticker)
    if (period == 'quater'):
        cf = ticker.cash_flow(trailing=True,frequency='q')
    else:
        cf = ticker.cash_flow(trailing=True,frequency='a')

    stat = []
    ls = cf.to_dict('dict')
    for i in ls:
        ls[i]['date'] = str(i)
        st = {}
        for key in ls[i]:
            st[key] = ls[i][key]
        stat.append(st)

    for st in stat:
        # Capital Expenditure
        # Operating Cash Flow
        # Depreciation & Amortization
        st["Depreciation & Amortization"] = st["Depreciation And Amortization"]
        if (not isFloat(st["Depreciation & Amortization"]) or
                not isFloat(st["Capital Expenditure"]) or
                not isFloat(st["Operating Cash Flow"])):
            stat.remove(st)


    cache_response(ticker, stat, statementName, tickerName, period)
    return stat


def get_income_statement_yf(ticker, period='annual', statementName='income_statment', tickerName=''):
    # ticker = yf.Ticker(ticker)
    if (period == 'quater'):
        inc = ticker.quarterly_incomestmt
    else:
        inc = ticker.income_stmt

    stat = []
    ls = inc.to_dict('dict')
    for i in ls:
        ls[i]['date'] = str(i)
        st = {}
        for key in ls[i]:
            st[key] = ls[i][key]
        stat.append(st)

    fast_inf = ticker.financials

    for st in stat:
        st["Income Tax Expense"] = st["Tax Provision"]
        st["Earnings before Tax"] = st["Pretax Income"]
        stat.remove(st)

    cache_response(ticker, stat, statementName, tickerName, period)
    return stat


def get_balance_statement_yf(ticker, period='annual', statementName='balance_statment',tickerName=''):
    # ticker = yf.Ticker(ticker)
    if (period == 'quater'):
        bs = ticker.quarterly_balancesheet
    else:
        bs = ticker.balancesheet

    stat = []
    ls = bs.to_dict('dict')
    for i in ls:
        ls[i]['date'] = str(i)
        st = {}
        for key in ls[i]:
            st[key] = ls[i][key]
        stat.append(st)

    for st in stat:
        st['Total assets'] = st['Total Assets']
        st['Total non-current assets'] = st['Total Non Current Assets']

    cache_response(ticker, stat, statementName, tickerName, period)
    return stat


def get_from_cache(ticker, statmentName, period):
    directory = ''
    if (not os.environ.get('cache_yq_dir') == ''):
        directory = os.environ.get('cache_yq_dir')
    fileName = statmentName + '-' + ticker + '.json'
    fileName = directory + "yf/" + period + "/" + fileName

    json_data = {}
    if os.path.exists(fileName):
        with open(fileName) as f:
            json_data = json.load(f)
        return json_data
    else:
        return None



def fetch_given_statement_yf(ticker, statementName, period, tickerName):
     stat = get_from_cache(tickerName, statementName, period)
     if(stat is None):
        if statementName == 'cashflow_statement':
            stat = get_cashflow_statement_yf(ticker, period, statementName, tickerName)
        elif statementName == 'income_statement':
            stat = get_income_statement_yf(ticker, period,statementName, tickerName)
        elif statementName == 'balance_statement':
            stat = get_balance_statement_yf(ticker, period,statementName, tickerName)

     return stat


def cache_response(ticker, data, statmentName, tickerName, period):
    # json_data = json.dumps(data, indent=4)
    directory = ''
    if (not os.environ.get('cache_yq_dir') == ''):
        directory = os.environ.get('cache_yq_dir')
    fileName = statmentName + '-' + tickerName + '.json'
    fileName = directory + 'yf/' + period + '/' +fileName

    with open(fileName, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def aggregate_quaterly_yearly(q_statement):
    yearly_statement = {}
    last_4_q_statement = q_statement[:4]
    count = 0
    for q_st in last_4_q_statement:
        for key in q_st:
            if(count == 0):
                yearly_statement[key] = q_st[key]
            else:
                if(type(q_st[key]) is float):
                    yearly_statement[key] = float(yearly_statement[key]) + q_st[key]
        count = count + 1

    result_statement = []
    result_statement.append(yearly_statement)
    for q_st in last_4_q_statement:
        result_statement.append(q_st)
    return result_statement

def get_availiable_shares(ticker_info):
    fast_info = ticker_info.fast_info
    return fast_info["shares"]

def get_share_info(ticker_info):
    share_info = ticker_info.info
    return share_info

