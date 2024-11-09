import json


class YahooQueryToFinanceMapper:
    def __init__(self, input_json):
        self.input_json = input_json

    def convert_cashflow(self):
        output_list = []
        lines = json.loads(self.input_json)
        for item in lines:
            input_dict = item

            output_dict = {
                "date": str(input_dict.get("asOfDate", "")),
                "Depreciation & Amortization": str(input_dict.get("DepreciationAndAmortization", "")),
                "Stock-based compensation": str(input_dict.get("StockBasedCompensation", "")),
                "Operating Cash Flow": str(input_dict.get("OperatingCashFlow", "")),
                "Capital Expenditure": str(input_dict.get("CapitalExpenditure", "")),
                "Acquisitions and disposals": str(input_dict.get("NetBusinessPurchaseAndSale", "")),
                "Investment purchases and sales": str(input_dict.get("NetInvestmentPurchaseAndSale", "")),
                "Investing Cash flow": str(input_dict.get("InvestingCashFlow", "")),
                "Issuance (repayment) of debt": str(input_dict.get("NetIssuancePaymentsOfDebt", "")),
                "Issuance (buybacks) of shares": str(input_dict.get("NetCommonStockIssuance", "")),
                "Dividend payments": str(input_dict.get("CashDividendsPaid", "")),
                "Financing Cash Flow": str(input_dict.get("FinancingCashFlow", "")),
                "Effect of forex changes on cash": str(input_dict.get("null", "")),
                "Net cash flow / Change in cash": str(input_dict.get("ChangesInCash", "")),
                "Free Cash Flow": str(input_dict.get("FreeCashFlow", "")),
                "Net Cash/Marketcap": str(input_dict.get("null", ""))
            }

            output_list.append(output_dict)

        return json.dumps(output_list, indent=4)

    def convert_bs(self,input_json):
        output_list = []
        input_array = json.loads(input_json)
        lines = json.loads(self.input_json)
        for item in lines:
            input_dict = item
            
            output_dict = {
                "date": str(input_dict.get("asOfDate", "")),
                "Cash and cash equivalents": str(input_dict.get("CashAndCashEquivalents", "")),
                "Short-term investments": str(input_dict.get("OtherShortTermInvestments", "")),
                "Cash and short-term investments": str(
                    input_dict.get("CashCashEquivalentsAndShortTermInvestments", "")),
                "Receivables": str(input_dict.get("Receivables", "")),
                "Inventories": str(input_dict.get("Inventory", "")),
                "Total current assets": str(input_dict.get("CurrentAssets", "")),
                "Property, Plant & Equipment Net": str(input_dict.get("NetPPE", "")),
                "Goodwill and Intangible Assets": str(input_dict.get("OtherNonCurrentAssets", "")),
                "Long-term investments": str(input_dict.get("InvestmentsAndAdvances", "")),
                "Tax assets": str(input_dict.get("TaxAssets", "")),
                "Total non-current assets": str(input_dict.get("TotalNonCurrentAssets", "")),
                "Total assets": str(input_dict.get("TotalAssets", "")),
                "Payables": str(input_dict.get("Payables", "")),
                "Short-term debt": str(input_dict.get("CurrentDebt", "")),
                "Total current liabilities": str(input_dict.get("CurrentLiabilities", "")),
                "Long-term debt": str(input_dict.get("LongTermDebt", "")),
                "Total debt": str(input_dict.get("TotalDebt", "")),
                "Deferred revenue": str(input_dict.get("CurrentDeferredRevenue", "")),
                "Tax Liabilities": "",
                "Deposit Liabilities": "",
                "Total non-current liabilities": str(
                    input_dict.get("TotalNonCurrentLiabilitiesNetMinorityInterest", "")),
                "Total liabilities": str(input_dict.get("TotalLiabilitiesNetMinorityInterest", "")),
                "Other comprehensive income": str(input_dict.get("GainsLossesNotAffectingRetainedEarnings", "")),
                "Retained earnings (deficit)": str(input_dict.get("RetainedEarnings", "")),
                "Total shareholders equity": str(input_dict.get("TotalEquityGrossMinorityInterest", "")),
                "Investments": str(input_dict.get("InvestmentinFinancialAssets", "")),
                "Net Debt": str(input_dict.get("NetDebt", "")),
                "Other Assets": str(input_dict.get("OtherNonCurrentAssets", "")),
                "Other Liabilities": str(input_dict.get("OtherNonCurrentLiabilities", ""))
            }

            output_list.append(output_dict)
        
        return json.dumps(output_list, indent=4)


    def convert_income_statement(this, input_json):
        json_array = json.loads(input_json)
        result = []
        for item in json_array:
            date = item["asOfDate"],
            revenue = item['OperatingRevenue']
            cost_of_revenue = item['CostOfRevenue']
            gross_profit = item['GrossProfit']
            rd_expenses = item['ResearchAndDevelopment']
            sg_and_a_expense = item['SellingGeneralAndAdministration']
            operating_expenses = item['TotalExpenses']
            operating_income = item['OperatingIncome']
            interest_expense = item['InterestExpense']
            earnings_before_tax = item['PretaxIncome']
            income_tax_expense = item['TaxProvision']
            net_income = item['NetIncome']
            weighted_avg_shs_out = item['DilutedAverageShares']
            eps = item['DilutedEPS']

            data = {
                "date": date,
                "Revenue": str(revenue),
                "Revenue Growth": "",
                "Cost of Revenue": str(cost_of_revenue),
                "Gross Profit": str(gross_profit),
                "R&D Expenses": str(rd_expenses),
                "SG&A Expense": str(sg_and_a_expense),
                "Operating Expenses": str(operating_expenses),
                "Operating Income": str(operating_income),
                "Interest Expense": str(interest_expense),
                "Earnings before Tax": str(earnings_before_tax),
                "Income Tax Expense": str(income_tax_expense),
                "Net Income - Non-Controlling int": "",
                "Net Income - Discontinued ops": "",
                "Net Income": str(net_income),
                "Preferred Dividends": "",
                "Net Income Com": str(net_income),
                "EPS": str(eps),
                "EPS Diluted": str(eps),
                "Weighted Average Shs Out": str(weighted_avg_shs_out),
                "Weighted Average Shs Out (Dil)": str(weighted_avg_shs_out),
                "Dividend per Share": "",
                "Gross Margin": str(gross_profit / revenue),
                "EBITDA Margin": str(item['EBITDA'] / revenue) if item['EBITDA'] is not None else "",
                "EBIT Margin": "",
                "Profit Margin": str(net_income / revenue),
                "Free Cash Flow margin": "",
                "EBITDA": str(item['EBITDA']) if item['EBITDA'] is not None else "",
                "EBIT": str(item['EBIT']),
                "Consolidated Income": "",
                "Earnings Before Tax Margin": str(earnings_before_tax / revenue),
                "Net Profit Margin": str(net_income / revenue),
            }

            result.append(data)

        return result