# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import trade_scan_libraries as tsl


def main1(driver, path, market):

    tsl.notice_start(market["name"])

    # Extract market data into dataframe
    df = tsl.extract_all(driver, market["url"])
    tsl.info_data_extracted()

    # Clean dataframe
    df = tsl.clean_all(df, market["currency"])
    tsl.info_data_cleaned()

    # Save to .csv file
    try:
        output_path = path
        output_name = market["output_name"]
        df.to_csv(tsl.os.path.join(output_path, output_name))
        tsl.notice_save_success(market["output_name"])

    except:
        tsl.error_save_failed(market["output_name"])


def main2(driver, path):

    tsl.notice_start("Cryptocurrency")

    # Extract market data into dataframe
    df = tsl.extract_crypto(driver)
    tsl.info_data_extracted()

    # Clean dataframe
    df = tsl.clean_all(df, " USD")
    tsl.info_data_cleaned()

    # Save to .csv file
    try:
        output_path = path
        output_name = f"crypto-market-{tsl.get_datetime()}.csv"
        df.to_csv(tsl.os.path.join(output_path, output_name))
        tsl.notice_save_success(output_name)

    except:
        tsl.error_save_failed(output_name)


# %% Pre-defined information
us_market_info = {"url": "https://www.tradingview.com/markets/stocks-usa/market-movers-all-stocks/",
                  "name": "USA Market", "currency": " USD", 
                  "config": "output_path_us", "output_name": f"stock-market-us-{tsl.get_date()}.csv"}

ca_market_info = {"url": "https://www.tradingview.com/markets/stocks-canada/market-movers-all-stocks/",
                  "name": "Canadian Market", "currency": " CAD", 
                  "config": "output_path_ca", "output_name": f"stock-market-ca-{tsl.get_date()}.csv"}

zh_market_info = {"url": "https://www.tradingview.com/markets/stocks-china/market-movers-all-stocks/",
                  "name": "Chinese Market", "currency": " CNY", 
                  "config": "output_path_zh", "output_name": f"stock-market-zh-{tsl.get_date()}.csv"}

hk_market_info = {"url": "https://www.tradingview.com/markets/stocks-hong-kong/market-movers-all-stocks/",
                  "name": "Hong Kong Market", "currency": " HKD", 
                  "config": "output_path_hk", "output_name": f"stock-market-hk-{tsl.get_date()}.csv"}

