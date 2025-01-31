
  
  
    



# DCF: Discounted Cash Flow

  This is the fork from https://github.com/halessi/DCF
    1. I added ability to calculate DCFs with multiple stock from a CSV file and provides output to CSV
      which can be used for comparison
    2. Added ability to calculate DCFs based on Yearly and Quaterly data
    3. Added feature to use YF data , also added Cache to avoid unnecessary API calls
    4. Removed Plotting capability as CSV table of comparing is good enough



## Usage
  Argument              | Usage          
----------------------- | ------------------
period                  | how many years to directly forecast [Free Cash Flows](https://financeformulas.net/Free-Cash-Flow-to-Firm.html)
ticker                  | ticker of the company, used for pulling financials
years                   | if computing historical DCFs (i.e. years > 1), the number of years back to compute
interval                | can compute DCFs historically on either an 'annual' or 'quarter' basis. if quarter is indicated, total number of DCFS = years * 4
step_increase           | __some sensitivity analysis__: if this is specified, DCFs will be computed for default + (step_increase * interval_number), showing specifically how changing the underlying assumption impacts valuation
steps                   | number of steps to take (for step_increase)
variable                | the variable to increase each step, those available are: earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, discount_rate, [more to come..]
discount_rate           | specified discount_rate (W.A.C.C., it'd be nice (i think) if we dynamically calculated this)
earnings_growth_rate    | specified rate of earnings growth (EBIT)
perpetual_growth_rate   | specified rate of perpetual growth for calculating terminal value after __period__ years, EBITDA multiples coming
apikey                  | (Free) API Key to access financial data from [financialmodelingprep](https://financialmodelingprep.com/) -- Can also be provided as `APIKEY` envrionment variable.

### Sample CSV Output Report
| Date       | Ticker | Current Price | Avg Growth | Avg Capex | Forecasted Share Price (Avg Growth) | EG Growth | Forecasted Share Price (EG Growth) | Forecasted Share Price (Quarterly Growth) |
|------------|--------|---------------|------------|-----------|-------------------------------------|-----------|------------------------------------|-------------------------------------------|
| 2023-08-31 | COST   | 734.80        | 0.1553     | 0.1574    | 155.83                              | 0.2       | 216.13                             |                                           |
| 2023-01-31 | KR     | 56.55         | -0.3488    | 0.0449    | -55.91                              | 0.1       | 56.15                              |                                           |
| 2023-12-31 | SFM    | 63.59         | -0.1276    | 0.2892    | -65.65                              | 0.2       | 106.85                             |                                           |
| 2023-09-30 | AAPL   | 172.28        | 0.1198     | 0.1687    | 92.20                               | 0.1       | 87.28                              |                                           |
| 2023-06-30 | MSFT   | 428.74        | 0.1048     | 0.2235    | 57.62                               | 0.1       | 118.59                             |                                           |


# My Changes to the existing repo

  **Added below Flag**

 Argument              | Usage          
----------------------- | ------------------
--p\
10\
--aveg\
True\
--uavg\
True\
--uf\
True\
--i\
annual\
--y\
1\
--eg\
0.10\
--d\
0.10\
--cg\
0.045\
--pg\
0.025\
--apikey\
blaw


### References

[1] http://people.stern.nyu.edu/adamodar/pdfiles/eqnotes/dcfcf.pdf                                                      
[2] http://people.stern.nyu.edu/adamodar/pdfiles/basics.pdf                                                     
[3] https://www.oreilly.com/library/view/valuation-techniques-discounted/9781118417607/xhtml/sec30.html                     
[4] https://www.cchwebsites.com/content/calculators/BusinessValuation.html
