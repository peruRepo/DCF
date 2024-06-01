import argparse, traceback
from decimal import Decimal

from modeling.data import *
import numpy as np
from dateutil.parser import parse
from modeling.AverageUtil import *
from repository.FinancialDataRepo import *
from datetime import datetime

from repository.YahooQueryDataRepo import get_EV_statement_yf
from utility.CommonUtil import isFloat


def DCF(ticker, ev_statement, income_statement, balance_statement, cashflow_statement, discount_rate,
        forecast, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, givenEbit, useAverage):
    """
    a very basic 2-stage DCF implemented for learning purposes.
    see enterprise_value() for details on arguments.

    args:
        see enterprise value for more info...

    returns:
        dict: {'share price': __, 'enterprise_value': __, 'equity_value': __, 'date': __}
        CURRENT DCF VALUATION. See historical_dcf to fetch a history.

    """
    enterprise_val = enterprise_value(income_statement,
                                      cashflow_statement,
                                      balance_statement,
                                      forecast,
                                      discount_rate,
                                      earnings_growth_rate,
                                      cap_ex_growth_rate,
                                      perpetual_growth_rate,
                                      givenEbit,
                                      useAverage)

    equity_val, share_price = equity_value(enterprise_val,
                                           ev_statement, balance_statement)

    print('\nEnterprise Value for {}: ${}.'.format(ticker, '%.2E' % Decimal(str(enterprise_val))),
          '\nEquity Value for {}: ${}.'.format(ticker, '%.2E' % Decimal(str(equity_val))),
          '\nPer share value for {}: ${}.\n'.format(ticker, '%.2E' % Decimal(str(share_price))),
          )

    return {
        'date': income_statement[0]['date'],  # statement date used
        'Ticker': ticker,
        'earnings_growth_rate': earnings_growth_rate,  # earning growth used
        # 'enterprise_value': enterprise_val,
        # 'equity_value': equity_val,
        'forecasted_share_price': share_price
    }


def historical_DCF(ticker, years, forecast, discount_rate, earnings_growth_rate,
                   cap_ex_growth_rate, perpetual_growth_rate, interval='annual', apikey='', givenEbit=0.0,
                   useAverage=False):
    """
    Wrap DCF to fetch DCF values over a historical timeframe, denoted period.

    args:
        same as DCF, except for
        period: number of years to fetch DCF for

    returns:
        {'date': dcf, ..., 'date', dcf}
    """
    dcfs = {}
    ticker_info = get_stock_info_yf(ticker)
    if (interval == 'quater'):

        income_statement = aggregate_quaterly_yearly(
            fetch_given_statement_yf(ticker=ticker_info, statementName="income_statement", period=interval,
                                     tickerName=ticker))
        balance_statement = aggregate_quaterly_yearly(
            fetch_given_statement_yf(ticker=ticker_info, statementName="balance_statement", period=interval,
                                     tickerName=ticker))
        cashflow_statement = aggregate_quaterly_yearly(
            fetch_given_statement_yf(ticker=ticker_info, statementName="cashflow_statement", period=interval,
                                     tickerName=ticker))
        # Below statment get the data from FM
        # enterprise_value_statement = get_EV_statement(ticker=ticker, period='annual', apikey=apikey)['enterpriseValues']
        enterprise_value_statement = get_EV_statement_yf(ticker_info, balance_statement)
    else:
        # Activate for FM  when Yahoo finance fails
        # income_statement = get_income_statement(ticker=ticker, period=interval, apikey=apikey)['financials']
        # balance_statement = get_balance_statement(ticker=ticker, period=interval, apikey=apikey)['financials']
        # cashflow_statement = get_cashflow_statement(ticker=ticker, period=interval, apikey=apikey)['financials']
        # enterprise_value_statement = get_EV_statement(ticker=ticker, period=interval, apikey=apikey)['enterpriseValues']
        # enterprise_value_statement[0]["Number of Shares"] = get_availiable_shares(ticker_info)
        #  Activate below for YF
        income_statement =  fetch_given_statement_yf(ticker=ticker_info, statementName="income_statement", period=interval,
                                     tickerName=ticker)
        balance_statement =   fetch_given_statement_yf(ticker=ticker_info, statementName="balance_statement", period=interval,
                                     tickerName=ticker)
        cashflow_statement =  fetch_given_statement_yf(ticker=ticker_info, statementName="cashflow_statement", period=interval,
                                     tickerName=ticker)
        enterprise_value_statement = get_EV_statement_yf(ticker_info, balance_statement)



    if interval == 'quater':
        intervals = years * 4
    else:
        intervals = years

    if interval == 'quater':
        # for interval in range(0, intervals):
        try:
            dcf = DCF(ticker,
                      enterprise_value_statement[0],
                      income_statement,  # pass year + 1 bc we need change in working capital
                      balance_statement,
                      cashflow_statement,
                      discount_rate,
                      forecast,
                      earnings_growth_rate,
                      cap_ex_growth_rate,
                      perpetual_growth_rate,
                      givenEbit,
                      useAverage)
        except (Exception, IndexError) as e:
            print(traceback.format_exc())
            print('Interval {} unavailable, no historical statement.'.format(interval))  # catch
        # else: dcfs[dcf['date']] = dcf
        print('-' * 60)
        # return dcfs
        return dcf
    else :
    # intervals = 1
        for interval in range(0, intervals):
            try:
                dcf = DCF(ticker,
                          enterprise_value_statement[0],
                          income_statement[interval:interval + 5],  # pass year + 1 bc we need change in working capital
                          balance_statement[interval:interval + 5],
                          cashflow_statement[interval:interval + 5],
                          discount_rate,
                          forecast,
                          earnings_growth_rate,
                          cap_ex_growth_rate,
                          perpetual_growth_rate,
                          givenEbit,
                          useAverage)
            except (Exception, IndexError) as e:
                print(traceback.format_exc())
                print('Interval {} unavailable, no historical statement.'.format(interval))  # catch
            # else: dcfs[dcf['date']] = dcf
            print('-' * 60)
        # return dcfs
        return dcf


def ulFCF(ebit, tax_rate, non_cash_charges, cwc, cap_ex):
    """
    Formula to derive unlevered free cash flow to firm. Used in forecasting.

    args:
        ebit: Earnings before interest payments and taxes.
        tax_rate: The tax rate a firm is expected to pay. Usually a company's historical effective rate.
        non_cash_charges: Depreciation and amortization costs.
        cwc: Annual change in net working capital.
        cap_ex: capital expenditures, or what is spent to maintain zgrowth rate.

    returns:
        unlevered free cash flow
    """

    return ebit * (1 - tax_rate) + abs(non_cash_charges) - abs(cwc) - abs(cap_ex)
    # return ebit * (1 - tax_rate) + non_cash_charges + cwc + cap_ex


def get_discount_rate():
    """
    Calculate the Weighted Average Cost of Capital (WACC) for our company.
    Used for consideration of existing capital structure.

    args:

    returns:
        W.A.C.C.
    """
    return .1  # TODO: implement


def equity_value(enterprise_value, enterprise_value_statement):
    """
    Given an enterprise value, return the equity value by adjusting for cash/cash equivs. and total debt.

    args:
        enterprise_value: (EV = market cap + total debt - cash), or total value
        enterprise_value_statement: information on debt & cash

    returns:
        equity_value: (enterprise value - debt + cash)
        share_price: equity value/shares outstanding
    """

    equity_val = enterprise_value
    # equity_val = enterprise_value - enterprise_value_statement['+ Total Debt']
    # equity_val += enterprise_value_statement['- Cash & Cash Equivalents']
    share_price = equity_val / float(enterprise_value_statement['Number of Shares'])

    return equity_val, share_price

def equity_value(enterprise_value, enterprise_value_statement, balance_statement):
    """
    Given an enterprise value, return the equity value by adjusting for cash/cash equivs. and total debt.

    args:
        enterprise_value: (EV = market cap + total debt - cash), or total value
        enterprise_value_statement: information on debt & cash

    returns:
        equity_value: (enterprise value - debt + cash)
        share_price: equity value/shares outstanding
    """

    equity_val = enterprise_value
    # equity_val = enterprise_value - enterprise_value_statement['+ Total Debt']
    # equity_val += enterprise_value_statement['- Cash & Cash Equivalents']
    share_price = equity_val / float(enterprise_value_statement['Number of Shares'])

    return equity_val, share_price

def enterprise_value(income_statement, cashflow_statement, balance_statement, period,
                     discount_rate, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, givenEbit,
                     useAverage):
    """
    Calculate enterprise value by NPV of explicit _period_ free cash flows + NPV of terminal value,
    both discounted by W.A.C.C.

    args:
        ticker: company for forecasting
        period: years into the future
        earnings growth rate: assumed growth rate in earnings, YoY
        cap_ex_growth_rate: assumed growth rate in cap_ex, YoY
        perpetual_growth_rate: assumed growth rate in perpetuity for terminal value, YoY

    returns:
        enterprise value
    """
    # XXX: statements are returned as historical list, 0 most recent

    if (useAverage):
        income_statement = find_average_each_element(income_statement);
        cashflow_statement = find_average_each_element(cashflow_statement);
        balance_statement = find_average_each_element(balance_statement);
        if income_statement[0]['EBIT']:
            ebit = float(income_statement[0]['EBITDA']) - float(cashflow_statement[0]['Depreciation & Amortization'])
            ebit = float(income_statement[0]['EBIT'])
        elif givenEbit != 0:
            ebit = givenEbit
        else:
            raise Exception("EBIT is missing")

        tax_rate = float(income_statement[0]['Income Tax Expense']) / \
                   float(income_statement[0]['Earnings before Tax'])
        non_cash_charges = float(cashflow_statement[0]['Depreciation & Amortization'])
        cwc = (float(balance_statement[0]['Total assets']) - float(
            balance_statement[0]['Total non-current assets'])) - \
              (float(balance_statement[0]['Total assets']) - float(balance_statement[0]['Total non-current assets']))
        cap_ex = float(cashflow_statement[0]['Capital Expenditure'])
        discount = discount_rate
    else:
        if income_statement[0]['EBIT']:
            ebit = float(income_statement[0]['EBIT'])
        elif givenEbit != 0:
            ebit = givenEbit
        # else:
        #     ebit = float(input(f"EBIT missing. Enter EBIT on {income_statement[0]['date']} or skip: "))
        else:
            raise Exception("EBIT is missing")

        tax_rate = float(income_statement[0]['Income Tax Expense']) / \
                   float(income_statement[0]['Earnings before Tax'])
        non_cash_charges = float(cashflow_statement[0]['Depreciation & Amortization'])
        cwc = (float(balance_statement[0]['Total assets']) - float(balance_statement[0]['Total non-current assets'])) - \
              (float(balance_statement[1]['Total assets']) - float(balance_statement[1]['Total non-current assets']))
        cap_ex = float(cashflow_statement[0]['Capital Expenditure'])
        discount = discount_rate

    flows = []
    print("earnings_growth_rate=", earnings_growth_rate)
    # Now let's iterate through years to calculate FCF, starting with most recent year
    print('Forecasting flows for {} years out, starting at {}.'.format(period, income_statement[0]['date']),
          ('\n         DFCF   |    EBIT   |    D&A    |    CWC     |   CAP_EX   | '))
    skip_count = 0
    for yr in range(1, period + 1):
        # increment each value by growth rate
        # ebit = ebit * (1 + (yr * earnings_growth_rate))
        ebit = ebit * (1 + (earnings_growth_rate))
        # non_cash_charges = non_cash_charges * (1 + (yr * earnings_growth_rate))
        # non_cash_charges = non_cash_charges * (1 + (yr * earnings_growth_rate))
        non_cash_charges = non_cash_charges * (1 + (earnings_growth_rate))
        cwc = cwc * 0.7  # TODO: evaluate this cwc rate? 0.1 annually?
        # cap_ex = cap_ex * (1 + (yr * cap_ex_growth_rate))
        cap_ex = cap_ex * (1 + (cap_ex_growth_rate))
        # discount by WACC
        flow = ulFCF(ebit, tax_rate, non_cash_charges, cwc, cap_ex)
        # Verify
        PV_flow = flow / ((1 + discount) ** yr)
        skip_count = skip_count + 1;
        # skip until 2022
        # if(skip_count > 2):
        flows.append(PV_flow)

        print(str(int(income_statement[0]['date'][0:4]) + yr) + '  ',
              '%.2E' % Decimal(PV_flow) + ' | ',
              '%.2E' % Decimal(ebit) + ' | ',
              '%.2E' % Decimal(non_cash_charges) + ' | ',
              '%.2E' % Decimal(cwc) + ' | ',
              '%.2E' % Decimal(cap_ex) + ' | ')

    NPV_FCF = sum(flows)

    # now calculate terminal value using perpetual growth rate
    final_cashflow = flows[-1] * (1 + perpetual_growth_rate)
    TV = final_cashflow / (discount - perpetual_growth_rate)
    NPV_TV = TV / (1 + discount) ** (1 + period)
    return NPV_TV + NPV_FCF


def enterprise_value_from_free_cash_flow(income_statement, cashflow_statement, balance_statement, period,
                                         discount_rate, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate,
                                         givenEbit):
    # final_cashflow = flows[-1] * (1 + perpetual_growth_rate)
    # TV = final_cashflow/(discount - perpetual_growth_rate)
    # NPV_TV = TV/(1+discount)**(1+period)

    return 0


def calculate_avg_growth(cashflow_statement):
    financials = cashflow_statement
    prev = 0.0
    growthPC = []
    for financial in reversed(financials):
        if (parse(financial["date"]) > parse('2010-12-31')):
            if (prev != 0.0):
                growthPC.append((Decimal(financial["Free Cash Flow"]) - prev) / prev)
            prev = Decimal(financial["Free Cash Flow"])
    arr = np.array(growthPC)
    convertedPC = arr.astype(np.float)
    print("Average Free cashflow growth=" + str(np.average(convertedPC)))


def calculate_avg_growth_from_ticker(ticker, interval, apikey):
    # cf_statements = get_cashflow_statement(ticker=ticker, period=interval, apikey=apikey)['financials']
    # bal_statements = get_balance_statement(ticker=ticker, period=interval, apikey=apikey)['financials'][::-1]
    # inc_statements = get_income_statement(ticker=ticker, period=interval, apikey=apikey)['financials'][::-1]
    ticker_info = get_stock_info_yf(ticker)
    cf_statements = fetch_given_statement_yf(ticker=ticker_info, statementName="cashflow_statement",
                                                  period=interval,
                                                  tickerName=ticker)

    prev = float(0.0)
    growthPC = []

    count = 0;

    for cf in reversed(cf_statements):
        if (parse(cf["date"]) > parse('2010-01-01')):
            # Nan Check for Free Cash Flow
            print(cf["Free Cash Flow"])
            if not isFloat(cf["Free Cash Flow"]):
                continue
            free_cash_flow = float(cf["Free Cash Flow"])
            # free_cash_flow = calculate_free_cash_flow(cf_statements[count-2:count], bal_statements[count-2:count], inc_statements[count])
            if (prev != 0.0):
                growthPC.append((free_cash_flow - prev) / prev)
            prev = free_cash_flow
        count = count + 1;

    a = sum(growthPC)
    b = len(growthPC)
    avg = a / b;
    print("Average Free cashflow growth=" + str(avg))
    return avg


def calculate_free_cash_flow(cashflow_statement,balance_statement,income_statement):
    # ebit = float(income_statement['EBIT'])
    ebit = float(income_statement['EBITDA']) - float(cashflow_statement[1]['Depreciation & Amortization'])
    tax_rate = float(income_statement['Income Tax Expense']) / \
               float(income_statement['Earnings before Tax'])
    non_cash_charges = float(cashflow_statement[1]['Depreciation & Amortization'])
    cwc = (float(balance_statement[1]['Total assets']) - float(balance_statement[1]['Total non-current assets'])) - \
          (float(balance_statement[0]['Total assets']) - float(balance_statement[0]['Total non-current assets']))
    cap_ex = float(cashflow_statement[1]['Capital Expenditure']) - float(cashflow_statement[0]['Capital Expenditure'])
    # As Per https://www.investopedia.com/terms/f/freecashflow.asp
    free_cash_flow = ebit * (1 - tax_rate) + abs(non_cash_charges) - abs(cwc) - abs(cap_ex)
    return free_cash_flow

def calculate_avg_capitol_exp_from_ticker(ticker, interval, apikey):
    ticker_info = get_stock_info_yf(ticker)
    financials = fetch_given_statement_yf(ticker=ticker_info, statementName="cashflow_statement",
                                                  period=interval,
                                                  tickerName=ticker)
    # financials = get_cashflow_statement(ticker=ticker, period=interval, apikey=apikey)['financials']
    prev = 0.0
    growthPC = []
    for financial in reversed(financials):
        if not isFloat(financial["Capital Expenditure"]):
            continue
        if (parse(financial["date"]) > parse('2015-01-01')):
            if (prev != 0.0):
                growthPC.append((float(financial["Capital Expenditure"]) - prev) / prev)
            prev = float(financial["Capital Expenditure"])
    a = sum(growthPC)
    b = len(growthPC)
    avg = sum(growthPC) / len(growthPC)
    print("Average CapEx Growth=" + str(avg))
    return avg






