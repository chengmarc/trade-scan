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
    print("")
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


# %% Functions for dataframe operation
  
    
def df_remove_duplicate(df:pd.DataFrame) -> pd.DataFrame:
    df_transposed = df.T
    df_transposed['index']=df_transposed.index
    index = df_transposed.pop('index')
    df_transposed.insert(0, 'index', index)
    df_transposed = df_transposed.drop_duplicates(subset='index', keep='first')
    df_transposed.pop('index')
    df = df_transposed.T
    print(Fore.WHITE + "Removed duplicated columns.")
    return df
    
    
def df_fill_empty_cells(df:pd.DataFrame) -> pd.DataFrame:
    df = df.replace("—", "N/A")
    df = df.replace("", "—")
    print(Fore.WHITE + "Filled up empty cells.")
    return df
    
    
def df_substitute_minus(df:pd.DataFrame) -> pd.DataFrame:    
    for column in df:
        df[column] = df[column].replace("−", "-", regex=True)
    print(Fore.WHITE + "Replaced U+2212 with U+002D.")
    return df
    

# %% 
currency_list = [
    "Price", "Market cap", "EPS diluted(TTM)", "EV", "Dividends per share(FY)", "Dividends per share(FQ)", 
    "Revenue(TTM)", "Gross profit(TTM)", "Operating income(TTM)", "Net income(TTM)", "EBITDA(TTM)", 
    "Assets(FQ)", "Current assets(FQ)", "Cash on hand(FQ)", "Liabilities(FQ)", "Debt(FQ)", "Net debt(FQ)", "Equity(FQ)", 
    "Operating CF(TTM)", "Investing CF(TTM)", "Financing CF(TTM)", "Free cash flow(TTM)", "CAPEX(TTM)"]

substitue_list = [
    "Volume 1D", "Market cap", "EV", "Revenue(TTM)", "Gross profit(TTM)", "Operating income(TTM)", "Net income(TTM)", "EBITDA(TTM)", 
    "Assets(FQ)", "Current assets(FQ)", "Cash on hand(FQ)", "Liabilities(FQ)", "Debt(FQ)", "Net debt(FQ)", "Equity(FQ)", 
    "Operating CF(TTM)", "Investing CF(TTM)", "Financing CF(TTM)", "Free cash flow(TTM)", "CAPEX(TTM)"]

# %% Functions for column operation


def col_remove_currency(df:pd.DataFrame, column_list:list) -> pd.DataFrame:
    for column in column_list:
        df[column] = df[column].replace(" USD", "", regex=True)        
    print(Fore.WHITE + "Removed currency symbol.")
    return df
    
    
def cell_str_to_float(string:str) -> float:
    if string != "N/A":
        if string[-1] == 'K':              
            number = float(string[:-1])
            factor = 10**3
        elif string[-1] == 'M': 
            number = float(string[:-1])
            factor = 10**6
        elif string[-1] == 'B': 
            number = float(string[:-1])
            factor = 10**9            
        elif string[-1] == 'T': 
            number = float(string[:-1])
            factor = 10**12
        else: 
            number = float(string)
            factor = 1
        return number*factor
    else:
        return "N/A"


def col_transform_number(df:pd.DataFrame, column_list:list) -> pd.DataFrame:
    for column in column_list:
        df[column] = df[column].apply(cell_str_to_float)
    print(Fore.WHITE + "Transformed abbreviations to numbers.")
    
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
    config.read(os.path.join(path, "config.ini"))
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
