# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import trade_scan_libraries as tsl
from colorama import init, Fore
init()

# %% Parse html content
driver = tsl.driver
driver.get("https://www.tradingview.com/markets/stocks-usa/market-movers-all-stocks/")
tsl.click_load_more(driver)
tsl.notice_load_complete()

# %%
df_list = []
tab_list = ["overview", "performance", "valuation", "dividends", "profitability", 
            "incomeStatement", "balanceSheet", "cashFlow", "oscillators", "trendFollowing"]

for tab_name in tab_list:
    tsl.click_tab(driver, tab_name)
    html = driver.page_source
    soup = tsl.bs(html, "html.parser")
    headers = tsl.get_data_headers(soup)
    df = tsl.extract_dataframe(soup, headers)
    df_list.append(df)
    print(Fore.WHITE + f"Extracted dataframe for {tab_name}.")
    
df = tsl.pd.concat(df_list, axis=1)

# %%
df = tsl.remove_duplicate(df)

# %%
currency_list = ["Price", "Market cap", "EPS diluted(TTM)", "EV", "Dividends per share(FY)", "Dividends per share(FQ)", 
                 "Revenue(TTM)", "Gross profit(TTM)", "Operating income(TTM)", "Net income(TTM)", "EBITDA(TTM)",
                 "Assets(FQ)", "Current assets(FQ)", "Cash on hand(FQ)", "Liabilities(FQ)", "Debt(FQ)", "Net debt(FQ)", "Equity(FQ)", 
                 "Operating CF(TTM)", "Investing CF(TTM)", "Financing CF(TTM)", "Free cash flow(TTM)", "CAPEX(TTM)"]

df = tsl.remove_currency(df, currency_list)

# %%
substitue_list = ["Volume 1D", "Market cap", "EV", 
                  "Revenue(TTM)", "Gross profit(TTM)", "Operating income(TTM)", "Net income(TTM)", "EBITDA(TTM)",  
                  "Assets(FQ)", "Current assets(FQ)", "Cash on hand(FQ)", "Liabilities(FQ)", "Debt(FQ)", "Net debt(FQ)", "Equity(FQ)", 
                  "Operating CF(TTM)", "Investing CF(TTM)", "Financing CF(TTM)", "Free cash flow(TTM)", "CAPEX(TTM)"]

df = tsl.substitute_sign(df, substitue_list)

# %% Export data
try:
    output_path, valid = tsl.get_and_check_config("output_path_us", script_path)
    output_name = f"stock-market-us-{tsl.get_date()}.csv"
    df.to_csv(os.path.join(output_path, output_name))
    if valid:
        tsl.notice_save_desired()
    else:
        tsl.notice_save_default()

except:
    tsl.error_save_failed()

tsl.notice_exit()
