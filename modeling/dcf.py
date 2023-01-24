import argparse, traceback
from decimal import Decimal

from modeling.data import *
import numpy as np
from dateutil.parser import parse


def DCF(ticker, ev_statement, income_statement, balance_statement, cashflow_statement, discount_rate, forecast, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate,givenEbit):
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
                                        givenEbit)

    equity_val, share_price = equity_value(enterprise_val,
                                           ev_statement)

    print('\nEnterprise Value for {}: ${}.'.format(ticker, '%.2E' % Decimal(str(enterprise_val))), 
              '\nEquity Value for {}: ${}.'.format(ticker, '%.2E' % Decimal(str(equity_val))),
           '\nPer share value for {}: ${}.\n'.format(ticker, '%.2E' % Decimal(str(share_price))),
            )

    return {
        'date': income_statement[0]['date'],       # statement date used
        'Ticker' : ticker,
        'earnings_growth_rate' : earnings_growth_rate, # earning growth used
        # 'enterprise_value': enterprise_val,
        # 'equity_value': equity_val,
        'forecasted_share_price': share_price
    }


def historical_DCF(ticker, years, forecast, discount_rate, earnings_growth_rate,
                   cap_ex_growth_rate, perpetual_growth_rate, interval = 'annual', apikey = '', givenEbit= 0.0):
    """
    Wrap DCF to fetch DCF values over a historical timeframe, denoted period. 

    args:
        same as DCF, except for
        period: number of years to fetch DCF for

    returns:
        {'date': dcf, ..., 'date', dcf}
    """
    dcfs = {}

    income_statement = get_income_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    balance_statement = get_balance_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    cashflow_statement = get_cashflow_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    enterprise_value_statement = get_EV_statement(ticker = ticker, period = interval, apikey = apikey)['enterpriseValues']
    if interval == 'quarter':
        intervals = years * 4
    else:
        intervals = years
    # intervals = 1
    for interval in range(0, intervals):
        try:
            dcf = DCF(ticker, 
                    enterprise_value_statement[interval],
                    income_statement[interval:interval+2],        # pass year + 1 bc we need change in working capital
                    balance_statement[interval:interval+2],
                    cashflow_statement[interval:interval+2],
                    discount_rate,
                    forecast, 
                    earnings_growth_rate,  
                    cap_ex_growth_rate, 
                    perpetual_growth_rate,
                    givenEbit)
        except (Exception, IndexError) as e:
            print(traceback.format_exc())
            print('Interval {} unavailable, no historical statement.'.format(interval)) # catch
        # else: dcfs[dcf['date']] = dcf
        print('-'*60)
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

    return ebit * (1-tax_rate) + abs(non_cash_charges) - abs(cwc) - abs(cap_ex)
    # return ebit * (1 - tax_rate) + non_cash_charges + cwc + cap_ex


def get_discount_rate():
    """
    Calculate the Weighted Average Cost of Capital (WACC) for our company.
    Used for consideration of existing capital structure.

    args:
    
    returns:
        W.A.C.C.
    """
    return .1 # TODO: implement 


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
    equity_val = enterprise_value - enterprise_value_statement['+ Total Debt'] 
    equity_val += enterprise_value_statement['- Cash & Cash Equivalents']
    share_price = equity_val/float(enterprise_value_statement['Number of Shares'])

    return equity_val,  share_price


def enterprise_value(income_statement, cashflow_statement, balance_statement, period,
                     discount_rate, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, givenEbit):
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
    if income_statement[0]['EBIT']:
        ebit = float(income_statement[0]['EBIT'])
    elif givenEbit != 0 :
        ebit = givenEbit
    # else:
    #     ebit = float(input(f"EBIT missing. Enter EBIT on {income_statement[0]['date']} or skip: "))
    else:
        raise Exception("EBIT is missing")

    tax_rate = float(income_statement[0]['Income Tax Expense']) /  \
               float(income_statement[0]['Earnings before Tax'])
    non_cash_charges = float(cashflow_statement[0]['Depreciation & Amortization'])
    cwc = (float(balance_statement[0]['Total assets']) - float(balance_statement[0]['Total non-current assets'])) - \
          (float(balance_statement[1]['Total assets']) - float(balance_statement[1]['Total non-current assets']))
    cap_ex = float(cashflow_statement[0]['Capital Expenditure'])
    discount = discount_rate

    flows = []
    print("earnings_growth_rate=",earnings_growth_rate)
    # Now let's iterate through years to calculate FCF, starting with most recent year
    print('Forecasting flows for {} years out, starting at {}.'.format(period, income_statement[0]['date']),
         ('\n         DFCF   |    EBIT   |    D&A    |    CWC     |   CAP_EX   | '))
    for yr in range(1, period+1):    

        # increment each value by growth rate
        # ebit = ebit * (1 + (yr * earnings_growth_rate))
        ebit = ebit * (1 + (earnings_growth_rate))
        # non_cash_charges = non_cash_charges * (1 + (yr * earnings_growth_rate))
        # non_cash_charges = non_cash_charges * (1 + (yr * earnings_growth_rate))
        non_cash_charges = non_cash_charges * (1 + (earnings_growth_rate))
        cwc = cwc * 0.7                             # TODO: evaluate this cwc rate? 0.1 annually?
        # cap_ex = cap_ex * (1 + (yr * cap_ex_growth_rate))
        cap_ex = cap_ex * (1 + (cap_ex_growth_rate))
        # discount by WACC
        flow = ulFCF(ebit, tax_rate, non_cash_charges, cwc, cap_ex)
        # Verify
        PV_flow = flow/((1 + discount)**yr)
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
    TV = final_cashflow/(discount - perpetual_growth_rate)
    # Verify

    # NPV_TV = TV/(1+discount)**(1+period)
    NPV_TV = TV / (1 + discount) ** (1 + period)
    return NPV_TV+NPV_FCF
    # New Present Value (NPV) equivalent of Terminal Value (TV)
    #  Ref https://www.youtube.com/watch?v=lZzg8lPCY3g
    # i = 1
    # pv_flow = []
    # for flow in flows:
    #    pv_flow.append(flow/(1+discount)**i)
    #    i = i + 1
    #
    # final_pv_for_flow = TV * (1 + perpetual_growth_rate)
    # final_tv_for_pv_for_flow = final_pv_for_flow/(discount - perpetual_growth_rate)
    #
    # sum_pv_flow = sum(pv_flow)
    #
    # return final_tv_for_pv_for_flow + sum_pv_flow

def enterprise_value_from_free_cash_flow(income_statement, cashflow_statement, balance_statement, period,
                     discount_rate, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, givenEbit):


    # final_cashflow = flows[-1] * (1 + perpetual_growth_rate)
    # TV = final_cashflow/(discount - perpetual_growth_rate)
    # NPV_TV = TV/(1+discount)**(1+period)

    return 0

def calculate_avg_growth(cashflow_statement):
    financials = cashflow_statement
    prev = 0.0
    growthPC = []
    for financial in reversed(financials):
        if(parse(financial["date"]) > parse('2010-12-31')):
            if (prev != 0.0):
                growthPC.append((Decimal(financial["Free Cash Flow"]) - prev)/prev)
            prev = Decimal(financial["Free Cash Flow"])
    arr = np.array(growthPC)
    convertedPC = arr.astype(np.float)
    print("Average Free cashflow growth="+str(np.average(convertedPC)))

def calculate_avg_growth_from_ticker(ticker, interval, apikey):
    financials = get_cashflow_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    # starting_value = float(0)
    # end_value = float(0)
    # starting_year = 0
    # for financial in reversed(financials):
    #     if(parse(financial["date"]) > parse('2010-01-01')):
    #         if(starting_value == 0.0):
    #             starting_value = float(financial["Free Cash Flow"])
    #             starting_year = parse(financial["date"]).year
    #         end_value = end_value + float(financial["Free Cash Flow"])
    #         print(financial["Free Cash Flow"])
    #         end_year = parse(financial["date"]).year
    #
    # calc_year = end_year - starting_year
    # cagr = ((end_value /starting_value) ** (1/calc_year)) - 1
    # print("Average Free CashFlow Growth="+str(cagr))
    # return cagr;
    prev = float(0.0)
    growthPC = []
    for financial in reversed(financials):
        if(parse(financial["date"]) > parse('2010-01-01')):
            if (prev != 0.0):
                # if Decimal(financial["Free Cash Flow"]) < 0 or prev < 0:
                #     growth = (abs(Decimal(financial["Free Cash Flow"])) - abs(prev)) / abs(prev)
                #     if(growth > 0) :
                #         growth =  -1 * growth
                #     growthPC.append(growth)
                # else:
                    growthPC.append((float(financial["Free Cash Flow"]) - prev)/prev)
            prev = float(financial["Free Cash Flow"])
    a = sum(growthPC)
    b = len(growthPC)
    avg = a/b;
    print("Average Free cashflow growth="+str(avg))
    return avg

def calculate_avg_capitol_exp_from_ticker(ticker, interval, apikey):
    financials = get_cashflow_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    prev = 0.0
    growthPC = []
    for financial in reversed(financials):
        if(parse(financial["date"]) > parse('2010-01-01')):
            if (prev != 0.0):
                growthPC.append((float(financial["Capital Expenditure"]) - prev) / prev)
            prev = float(financial["Capital Expenditure"])
    a = sum(growthPC)
    b = len(growthPC)
    avg = sum(growthPC) / len(growthPC)
    print("Average CapEx Growth=" + str(avg))
    return avg
    # starting_value = 0
    # end_value = float(0)
    # starting_year = 0
    # for financial in reversed(financials):
    #     if(parse(financial["date"]) > parse('2010-01-01')):
    #         if(starting_value == 0.0):
    #             starting_value = float(financial["Capital Expenditure"])
    #             starting_year = parse(financial["date"]).year
    #         end_value = end_value + float(financial["Capital Expenditure"])
    #         print(financial["Capital Expenditure"])
    #         end_year = parse(financial["date"]).year
    #
    # calc_year = end_year - starting_year
    # cagr = ((end_value / starting_value ** 1 / calc_year)) - 1
    # print("Average CapEx Growth=" + str(cagr))
    # return cagr;






