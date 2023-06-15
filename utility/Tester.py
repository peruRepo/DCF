import yfinance as yf
import pandas as pd
from yahooquery import Ticker

#Yahoo Query

aapl = Ticker('aapl')
bs = aapl.balance_sheet(frequency="a", trailing=True)
print(bs.to_json('bs.json', orient='records', lines=True));
cf= aapl.cash_flow(trailing=True,frequency='q')
print(cf.to_json('cf.json', orient='records', lines=True));


# first stock
# ticker = yf.Ticker('AAPL')
# fast_inf = ticker.info
# print(fast_inf)
# period = 'quarterly'
# if (period == 'quarterly'):
#     cf = ticker.quarterly_incomestmt
# else:
#     cf = ticker.balancesheet
#
# ls=cf.to_dict('dict')
#
# for i in ls:
#     ls[i][str(i)]=str(i)
#     for key in ls[i]:
#         print(ls[i][key])



# print(ls)


