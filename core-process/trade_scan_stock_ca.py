# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os, time
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import trade_scan_libraries as tsl
from colorama import init, Fore
init()

# %% Parse html content
driver = tsl.driver
driver.get("https://www.tradingview.com/markets/stocks-canada/market-movers-all-stocks/")
tsl.click_load_more(driver)
print("")
print(Fore.GREEN + "All data loaded.")

# %% Main Execution
df_list = []
tab_list = [
    "overview", "performance", "valuation", "dividends", "profitability", 
    "incomeStatement", "balanceSheet", "cashFlow", "oscillators", "trendFollowing"]

for tab_name in tab_list:
    tsl.click_tab(driver, tab_name)
    html = driver.page_source
    soup = tsl.bs(html, "html.parser")
    headers = tsl.get_data_headers(soup)
    df = tsl.extract_dataframe(soup, headers)
    df_list.append(df)
    print(Fore.WHITE, f"- Extracted dataframe for {tab_name}.")
    time.sleep(3)
    
df = tsl.pd.concat(df_list, axis=1)
print("")
print(Fore.GREEN + "All data ready.")

# %% Data cleaning
df = df.map(lambda x: str(x))
df = tsl.df_remove_duplicate(df)
df = tsl.df_fill_empty_cells(df)
df = tsl.df_substitute_minus(df)

df = tsl.col_remove_currency(df, tsl.currency_list)
df = tsl.col_transform_number(df, tsl.substitue_list)

# %% Export data
try:
    output_path, valid = tsl.get_and_check_config("output_path_ca", os.path.dirname(script_path))
    output_name = f"stock-market-ca-{tsl.get_date()}.csv"
    df.to_csv(os.path.join(output_path, output_name))
    if valid:
        tsl.notice_save_desired()
    else:
        tsl.notice_save_default()

except:
    tsl.error_save_failed()

tsl.notice_exit()
