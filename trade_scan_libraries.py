# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 16:33:32 2023

@author: Admin
"""

import os, sys, time, datetime, configparser, getpass 

script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

try:
    import pandas as pd
    from bs4 import BeautifulSoup as bs
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "Core modules imported.")

except ImportError as e:
    print(f"The module '{e.name}' is not found, please install it using either pip or conda.")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()
    
# %%
def extract_dataframe(soup) -> pd.DataFrame:
    df_raw = soup.find_all("tr", class_="row-RdUXZpkv listRow")
    df_clean = pd.DataFrame(columns = ['Symbol', 'Company', 'Price', 'Change%1D', 'Change1D',
                                   'Volume1D', 'Volume*Price1D', 'MarketCap', 'MarketCapPerformance%1Y',
                                   'PriceEarningRatio', 'EarningPerShare(TTM)', 'Employees(FY)', 'Sector'])


    for row in df_raw:
        row_content = []
    
        cell_left = row.find('td', class_='cell-RLhfr_y4 left-RLhfr_y4 cell-fixed-ZtyEm8a1 onscroll-shadow')
        symbol = cell_left.find('a', class_='apply-common-tooltip tickerNameBox-GrtoTeat tickerName-GrtoTeat')
        name = cell_left.find('sup', class_='apply-common-tooltip tickerDescription-GrtoTeat')
        row_content.append(symbol.get_text())
        row_content.append(name.get_text())
    
        cells_mid = row.find_all('td', class_='cell-RLhfr_y4 right-RLhfr_y4')
        for cell_mid in cells_mid:
            row_content.append(cell_mid.get_text())
        
        cells_right = row.find_all('td', class_='cell-RLhfr_y4 left-RLhfr_y4')
        cell_right = cells_right[1]
        row_content.append(cell_right.get_text())
    
        df_clean.loc[len(df_clean)] = row_content
    
    return df_clean

def trim_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace("—", "N/A")

    # Remove USD currency symbol
    df['Price'] = df['Price'].str[:-4]
    df['Change1D'] = df['Change1D'].str[:-4]
    df['Volume*Price1D'] = df['Volume*Price1D'].str[:-4]
    df['MarketCap'] = df['MarketCap'].str[:-4]
    df['EarningPerShare(TTM)'] = df['EarningPerShare(TTM)'].str[:-4]

    # Replace "−" to "-"
    df['Change%1D'] = df['Change%1D'].str.replace("−", "-")
    df['Change1D'] = df['Change1D'].str.replace("−", "-")
    df['MarketCapPerformance%1Y'] = df['MarketCapPerformance%1Y'].str.replace("−", "-")
    df['EarningPerShare(TTM)'] = df['EarningPerShare(TTM)'].str.replace("−", "-")
    
    return df


def str_to_float(df, col_name: str) -> pd.DataFrame:
    for index, row in df.iterrows():
        container = df.loc[index, col_name]
        if len(container) != 0 and container[-1] == 'B': 
            df.loc[index, col_name] = float(container[:-1])*1000000000
        elif len(container) != 0 and container[-1] == 'M':
            df.loc[index, col_name] = float(container[:-1])*1000000
        elif len(container) != 0 and container[-1] == 'K':
            df.loc[index, col_name] = float(container[:-1])*1000
        elif len(container) != 0 and container[-1] in [n for n in range(10)]:
            df.loc[index, col_name] = float(container[:-1])
        else: df.loc[index, col_name] = "N/A"
    return df

# %% Function for output path and output time


def get_and_check_config(selection: str) -> (str, bool):
    """
    This function checks "trade_scan config.ini" and returns the path if there is one.
    If the path is empty or is not valid, then it will return the default path.

    Return:         a boolean that represents the validity
                    a string that represents the output path
    """
    config = configparser.ConfigParser()    
    config.read(r"trade_scan config.ini")
    config_path = config.get(r"Paths", selection)
    if os.path.isdir(config_path):
        return config_path, True
    elif selection == "output_path_us":
        return os.path.join(script_path, "market-data"), False
    elif selection == "output_path_ca":
        return os.path.join(script_path, "market-data"), False
    elif selection == "output_path_zh":
        return os.path.join(script_path, "market-data"), False
    elif selection == "output_path_hk":
        return os.path.join(script_path, "market-data"), False


def get_date():
    """
    This function returns a string that represents the current time.
    
    Return:         a string of the format: %Y-%m-%d_%H-%M-%S
    """
    current_datetime = datetime.datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d")
    return formatted_date


# %% Function for user notice


def notice_load_complete():
    print(Fore.GREEN + "  _                 _ _                                         _      _        ")
    print(Fore.GREEN + " | | ___   __ _  __| (_)_ __   __ _    ___ ___  _ __ ___  _ __ | | ___| |_ ___  ")
    print(Fore.GREEN + " | |/ _ \ / _` |/ _` | | '_ \ / _` |  / __/ _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \ ")
    print(Fore.GREEN + " | | (_) | (_| | (_| | | | | | (_| | | (_| (_) | | | | | | |_) | |  __/ ||  __/ ")
    print(Fore.GREEN + " |_|\___/ \__,_|\__,_|_|_| |_|\__, |  \___\___/|_| |_| |_| .__/|_|\___|\__\___| ")
    print(Fore.GREEN + "                              |___/                      |_|                    ")
    

def notice_save_desired():
    print("")
    print(Fore.WHITE + "Successfully loaded output config.")
    print(Fore.WHITE + "Data has been saved to the desired location.")
    print("")


def notice_save_default():
    print("")
    print(Fore.WHITE + "Output config not detected.")
    print(Fore.WHITE + "Data has been saved to the default location.")
    print("")


def notice_exit():
    print(Fore.WHITE + "Quit automatically in 20 seconds...")
    time.sleep(20)
    sys.exit()


def error_save_failed():
    print("")
    print(Fore.RED + "Failed to save extracted data, please troubleshoot.")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()

