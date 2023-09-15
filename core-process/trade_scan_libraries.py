# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os, sys, time, datetime, configparser, getpass
script_path = os.path.dirname(os.path.realpath(__file__))

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

import webdrivers.webdriver_initializer as webdriver
driver = webdriver.driver

# %% Functions for web interactions


def click_load_more(driver) -> None:
    timeout_times = 0
    while True:
        try:
            # Wait for up to 3 seconds for the button to be clickable
            driver.implicitly_wait(3)
            driver.find_element(webdriver.By.CLASS_NAME, "loadButton-SFwfC2e0").click()
            print(Fore.WHITE, "- Loading information...")
        except:
            # After repeated timeout we conclude that everything has been loaded
            timeout_times += 1
            if (timeout_times > 0): break
            else: continue


def click_tab(driver, tab_name:str) -> None:
    button = driver.find_element(webdriver.By.ID , tab_name)
    button.click()


# %% Functions for data extraction


def get_data_headers(soup) -> list:
    twarp = soup.find("div", class_="tableWrapSticky-SfGgNYTG")
    thead = twarp.find_all("th", class_="cell-seAzPAHn")
    headers = ['Symbol', 'Company']
    for field in thead[1:]:
        headers.append(field.get_text())
    return headers
    
def extract_dataframe(soup, headers:list) -> pd.DataFrame:        
    df = pd.DataFrame(columns=headers)
    trow = soup.find_all("tr", class_="row-RdUXZpkv listRow")
    for row in trow:
        row_content = []
        tdata = row.find_all("td", class_="cell-RLhfr_y4")
        
        symbol = tdata[0].find("a", class_="apply-common-tooltip tickerNameBox-GrtoTeat tickerName-GrtoTeat")
        name = tdata[0].find("sup", class_="apply-common-tooltip tickerDescription-GrtoTeat")
        row_content.append(symbol.get_text())
        row_content.append(name.get_text())        
        
        for field in tdata[1:]:
            row_content.append(field.get_text())
            
        df.loc[len(df)] = row_content
    return df


# %% Functions for data cleaning


def mark_NA(df:pd.DataFrame) -> pd.DataFrame:
    df_NA = df.replace("—", "N/A")
    return df_NA


def remove_duplicate(df:pd.DataFrame) -> pd.DataFrame:
    df_transposed = df.T
    df_transposed = df_transposed.drop_duplicates()
    return df_transposed.T  
    


def remove_currency(df:pd.DataFrame, column_list:list) -> pd.DataFrame:
    for column in column_list:
        df[column] = df[column].str[:-4]
    return df


def substitute_minus(df:pd.DataFrame, column_list:list) -> pd.DataFrame:    
    for column in column_list:
        df[column] = df[column].str.replace("−", "-")
    return df


def str_to_number(string:str) -> float:
    if string[-1] == 'K': factor = 10**3
    elif string[-1] == 'M': factor = 10**6
    elif string[-1] == 'B': factor = 10**9
    else: factor = 1
    number = float(string[:-1])
    return number*factor


def transform_number(df:pd.DataFrame, column_list:list) -> pd.DataFrame:
    for column in column_list:
        df[column] = df[column].str.replace("[KMB]","")
        df[column] = df[column].apply(str_to_number)
    return df


# %% Function for output path and output time


def get_and_check_config(selection: str, path:str) -> (str, bool):
    """
    This function checks "trade_scan config.ini" and returns the path if there is one.
    If the path is empty or is not valid, then it will return the default path.

    Return:         a boolean that represents the validity
                    a string that represents the output path
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(path, "trade_scan config.ini"))
    config_path = config.get("Paths", selection)
    if os.path.isdir(config_path):
        return config_path, True
    elif selection == "output_path_us":
        return os.path.join(path, "market-data", "us-market"), False
    elif selection == "output_path_ca":
        return os.path.join(path, "market-data", "ca-market"), False
    elif selection == "output_path_zh":
        return os.path.join(path, "market-data", "zh-market"), False
    elif selection == "output_path_hk":
        return os.path.join(path, "market-data", "hk-market"), False


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
