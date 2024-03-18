import yfinance as yf
import pandas as pd

from yahooquery import Ticker

from repository.YahooQueryToFinanceMapper import YahooQueryToFinanceMapper

#Yahoo Query

aapl = Ticker('aapl')
# bs = aapl.balance_sheet(frequency="a", trailing=True)
# print(bs.to_json('bs.json', orient='records', lines=True));
enterpriseValue= aapl.all_financial_data(frequency="q")
# converter = YahooQueryToFinanceMapper(cf.to_json(orient='records'))
# output_json = converter.convert_income_statement()
# ev = TotalCapitalization + TotalDebt
# CashAndCashEquivalents
# Market Capitalization = TotalCapitalization
#  BasicAverageShares
print(enterpriseValue.to_json('enp.json', orient='records', lines=True));


# print(output_json)

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


