# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os

script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import trade_scan_libraries as tsl
import webdrivers.webdriver_initializer as wd
from colorama import init, Fore
init()

# %% Parse html content
driver = wd.driver
driver.get("https://www.tradingview.com/markets/stocks-canada/market-movers-all-stocks/")
print("")

# Click the "Load More" button until everything is loaded
timeout_times = 0
while True:
    try:
        # Wait for up to 3 seconds for the button to be clickable
        driver.implicitly_wait(3)  
        driver.find_element(wd.By.CLASS_NAME, "loadButton-SFwfC2e0").click()
        print(Fore.WHITE, "Loading information...")
    except:
        # After repeated timeout we conclude that everything has been loaded
        timeout_times += 1
        if (timeout_times > 5):  
            tsl.notice_load_complete()
            break
        else:
            continue

html = driver.page_source
driver.quit()

# %% Extract and clean data
soup = tsl.bs(html, "html.parser")
df = tsl.extract_dataframe(soup)
print(Fore.WHITE + "Successfully extracted market data.")

df = tsl.trim_dataframe(df)
df = tsl.str_to_float(df, "Volume1D")
df = tsl.str_to_float(df, "Volume*Price1D")
df = tsl.str_to_float(df, "MarketCap")
df = tsl.str_to_float(df, "Employees(FY)")
print(Fore.WHITE + "Data cleaning completed.")

# %% Export data
try:
    output_path, valid = tsl.get_and_check_config("output_path_ca")
    output_name = f"stock-market-ca-{tsl.get_date()}.csv"
    df.to_csv(os.path.join(output_path, output_name))
    if valid:
        tsl.notice_save_desired()
    else:
        tsl.notice_save_default()

except:
    tsl.error_save_failed()

tsl.notice_exit()
