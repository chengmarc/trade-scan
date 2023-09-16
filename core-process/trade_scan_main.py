# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import trade_scan_libraries as tsl

# %% Pre-defined information
us_market_info = {"url": "https://www.tradingview.com/markets/stocks-usa/market-movers-all-stocks/",
                  "name": "US Market", "currency": " USD", 
                  "config": "output_path_us", "output_name": f"stock-market-us-{tsl.get_date()}.csv"}

ca_marekt_info = {"url": "https://www.tradingview.com/markets/stocks-canada/market-movers-all-stocks/",
                  "name": "Canadian Market", "currency": " CAD", 
                  "config": "output_path_ca", "output_name": f"stock-market-ca-{tsl.get_date()}.csv"}

zh_market_info = {"url": "https://www.tradingview.com/markets/stocks-china/market-movers-all-stocks/",
                  "name": "Chinese Market", "currency": " CNY", 
                  "config": "output_path_zh", "output_name": f"stock-market-zh-{tsl.get_date()}.csv"}

hk_market_info = {"url": "https://www.tradingview.com/markets/stocks-hong-kong/market-movers-all-stocks/",
                  "name": "Hong Kong Market", "currency": " HKD", 
                  "config": "output_path_hk", "output_name": f"stock-market-hk-{tsl.get_date()}.csv"}

# %% Main Execution
driver = tsl.driver
for market in [us_market_info, ca_marekt_info, zh_market_info, hk_market_info]:
    tsl.notice_start(market["name"])
    df = tsl.extract_all(driver, market["url"])
    df = tsl.clean_all(df, market["currency"])
    market["data"] = df
    try:
        output_path, valid = tsl.get_and_check_config(market["config"], os.path.dirname(script_path))
        output_name = market["output_name"]
        market["data"].to_csv(os.path.join(output_path, output_name))
        if valid:
            tsl.notice_save_desired(market["output_name"])
        else:
            tsl.notice_save_default(market["output_name"])
    except:
        tsl.error_save_failed(market["output_name"])
        
tsl.notice_exit()
