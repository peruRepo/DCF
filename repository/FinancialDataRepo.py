import yfinance as yf


def get_cashflow_statement(ticker, period='annual'):
    ticker = yf.Ticker(ticker)
    if(period=='quarterly'):
        cf = ticker.quarterly_cashflow
    else :
        cf = ticker.cashflow
    return cf

def get_income_statement(ticker, period='annual'):
    ticker = yf.Ticker(ticker)
    if(period=='quarterly'):
        cf = ticker.quarterly_incomestmt
    else :
        cf = ticker.income_stmt
    return cf


def get_balance_statement(ticker, period='annual'):
    ticker = yf.Ticker(ticker)
    if(period=='quarterly'):
        cf = ticker.quarterly_balancesheet
    else :
        cf = ticker.balancesheet
    return cf