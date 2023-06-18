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
