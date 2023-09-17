# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

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

import webdrivers.webdriver_initializer as webdriver
driver = webdriver.driver


# %% Function overview
"""
The graph below is an overview of the call structure of the functions.
│ 
├───extract_all()                   # core function for extraction
│   │
│   ├───click_load_more()           # dynamic interaction (load more)
│   ├───click_tab()                 # dynamic interaction (switch tab)
│   │
│   ├───get_data_headers()          # get headers for each tab
│   ├───extract_dataframe()         # dataframe extraction
│   │
│   ├───notice_data_loaded()        # user notice
│   └───notice_data_extracted()     # user notice
│
├───clean_all()                     # core function for data cleaning
│   │
│   ├───df_remove_duplicate()       # remove duplicated columns
│   ├───df_fill_empty_cells()       # fill empty cells to "N/A"
│   ├───df_substitute_minus()       # substitute "−" for "-"
│   │
│   ├───df_remove_currency()        # remove currency symbol
│   └───df_transform_number()       # transform abbreviations into float
│       │ 
│       └───cell_str_to_float()     # transform abbreviations into float
│           │ 
│           └───get_abbrev_list()   # produce a list of possible suffixes
│
├───get_and_check_config()          # set output path
├───get_date()                      # get current date
├───get_datetime()                  # get current datetime
│
├───notice_start()                  # user notice
├───notice_save_desired()           # user notice
├───notice_save_default()           # user notice
│
└───error_save_failed()             # user notice
"""

# %% Functions for web interactions


def click_load_more(driver) -> None:
    """
    The function takes a selenium webdriver and click the "load" button until everything is loaded.

    Precondition:   selenium webdriver has opened a TradingView market page
    """    
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
            if (timeout_times > 10): break
            else: continue


def click_tab(driver, tab_name: str) -> None:
    """
    The function takes a selenium webdriver and click the tab given.

    Precondition:   selenium webdriver has opened a TradingView market page
                    tab name is a valid id that represents a clickable object
    """
    button = driver.find_element(webdriver.By.ID , tab_name)
    button.click()


# %% Functions for data extraction


def get_data_headers(soup) -> list:
    """
    The function takes a BeautifulSoup object and return a list of headers.

    Precondition:   soup has been correctly parsed
    Return:         a list of headers

    #Example
    input:  a BeautifulSoup object parsed from:
            https://www.tradingview.com/markets/stocks-usa/market-movers-all-stocks/

    output: ["Price", "Change % 1D", "Volume 1D", "Market cap", "P/E", "EPS diluted (TTM)", 
             "EPS diluted growth % (TTM YoY)", "Dividend yield % (TTM)", "Sector", "Analyst Rating"]
    """
    twarp = soup.find("div", class_="tableWrapSticky-SfGgNYTG")
    thead = twarp.find_all("th", class_="cell-seAzPAHn")
    headers = ['Symbol', 'Company']
    for field in thead[1:]:
        headers.append(field.get_text())
    return headers


def extract_dataframe(soup, headers: list) -> pd.DataFrame:
    """
    The function takes a BeautifulSoup object and a list of headers to return a pandas dataframe.

    Precondition:   soup has been correctly parsed
                    headers is a list that matches the sheet headers
    Return:         a pandas dataframe containing the market data
    """
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


# %% Functions for dataframe cleaning 


def df_remove_duplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    The function takes a pandas dataframe and remove duplicate columns.
    
    Return:         a pandas dataframe with unique columns
    
    #Example
    input:  Name    Price   Price   Rating
            NVIDIA  400     400     Buy
            Meta    150     200     Sell
            
    output: Name    Price   Rating
            NVIDIA  400     Buy
            Meta    150     Sell
    """
    df_transposed = df.T
    df_transposed['index']=df_transposed.index
    index = df_transposed.pop('index')
    df_transposed.insert(0, 'index', index)
    df_transposed = df_transposed.drop_duplicates(subset='index', keep='first')
    df_transposed.pop('index')
    df = df_transposed.T
    print(Fore.WHITE + "Removed duplicated columns.")
    return df


def df_fill_empty_cells(df: pd.DataFrame) -> pd.DataFrame:
    """
    The function takes a pandas dataframe and fill in the empty cells.
    
    Return:         a pandas dataframe with no empty cells
    
    #Example
    input:  Name    Price   Rating
            NVIDIA          Buy
            Meta    150     —

    output: Name    Price   Rating
            NVIDIA  N/A     Buy
            Meta    150     N/A
    """
    df = df.replace("—", "N/A")
    df = df.replace("", "N/A")
    print(Fore.WHITE + "Filled up empty cells.")
    return df


def df_substitute_minus(df: pd.DataFrame) -> pd.DataFrame:
    """
    The function takes a pandas dataframe and fill in the empty cells.
    
    Return:         a pandas dataframe with no empty cells
    
    #Example
    input:  Name    Change  Rating
            NVIDIA  5%      Buy
            Meta    —10%    Sell

    output: Name    Change  Rating
            NVIDIA  5%      Buy
            Meta    -10%    Sell
    """
    for column in df:
        df[column] = df[column].replace("−", "-", regex=True)
    print(Fore.WHITE + "Replaced U+2212 with U+002D.")
    return df


def df_remove_currency(df: pd.DataFrame, string: str) -> pd.DataFrame:
    """
    The function takes a pandas dataframe and a replace string
    to replace all the occurrence of the given string in the given dataframe.
    
    Return:         a pandas dataframe where the given string is replaced
    
    #Example
    input:  the pandas dataframe shown below, " USD"
            Name    Price       Rating
            NVIDIA  400 USD     Buy
            Meta    150 USD     Sell

    output: Name    Price       Rating
            NVIDIA  400         Buy
            Meta    150         Sell
    """
    for column in df:
        df[column] = df[column].replace(string, "", regex=True)
    print(Fore.WHITE + "Removed currency symbol.")
    return df


def get_abbrev_list(abbrev: str) -> list:
    """
    The function produce a list of possible suffixes for number abbreviations.
    (note: this function is for one time execution only)
    """
    abbrev_list = []
    for character in abbrev:
        abbrev_list.extend([f"{i}{character}" for i in range(10)])
    return abbrev_list


abbrev_list = get_abbrev_list(["K","M","B","T"])


def cell_str_to_float(string: str) -> float:
    """
    The function takes a number abbreviation string and returns the number.

    Precondition:   string contains an abbreviated number: "10K", "20M", "30B", "40T"
    Return:         a float number such as 10000
    
    #Example
    input:  "768M"
    output: "768000000.00"
    """
    if string[-2:] in abbrev_list:
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
        return string


def df_transform_number(df: pd.DataFrame) -> pd.DataFrame:
    """
    The function takes a pandas dataframe and replace all number abbreviations to float numbers.
    
    Return:         a pandas dataframe where number abbreviations are replaced
    
    #Example
    input:  Name        MarketCap   Rating            
            Apple       400M        Buy
            Aerotyne    150K        Sell

    output: Name        MarketCap   Rating
            Apple       400000000   Buy
            Aerotyne    150000      Sell
    """
    for column in df:
        df[column] = df[column].apply(cell_str_to_float)
    print(Fore.WHITE + "Transformed abbreviations to numbers.")
    return df


# %% Function for output path and output time


def get_and_check_config(selection: str, path: str) -> (str, bool):
    """
    This function checks "config.ini" and returns the path if there is one.
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
    elif selection == "output_path_crypto":
        return os.path.join(path, "crypto-data"), False


def get_date() -> str:
    """
    This function returns a string that represents the current date.

    Return:         a string of the format: %Y-%m-%d
    """
    current_datetime = datetime.datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d")
    return formatted_date


def get_datetime() -> str:
    """
    This function returns a string that represents the current datetime.

    Return:         a string of the format: %Y-%m-%d_%H-%M-%S
    """
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    return formatted_datetime


# %% Function for user notice


def notice_start(market: str) -> None:
    length = len(market) + 12 + 6*2
    print("")
    print(Fore.WHITE + length*"#")
    print(Fore.WHITE + f"##### Execute for {market} #####")
    print(Fore.WHITE + length*"#")


def notice_data_loaded() -> None:
    print("")
    print(Fore.GREEN + "All data loaded.")
    print("")


def notice_data_extracted() -> None:
    print("")
    print(Fore.GREEN + "All data extracted.")
    print("")


def notice_save_desired(filename: str) -> None:
    print("")
    print(Fore.WHITE + "Successfully loaded output config.")
    print(Fore.WHITE + f"{filename} has been saved to the desired location.")
    print("")


def notice_save_default(filename: str) -> None:
    print("")    
    print(Fore.WHITE + "Output config not detected.")
    print(Fore.WHITE + f"{filename} has been saved to the default location.")
    print("")


def error_save_failed(filename: str) -> None:
    print("")
    print(Fore.RED + f"Failed to save {filename}")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()


# %% Pre-defined tab list
tab_list = ["overview", "performance", "valuation", "dividends", "profitability", 
            "incomeStatement", "balanceSheet", "cashFlow", "oscillators", "trendFollowing"]

# %% Core functions


def extract_all(driver, url:str) -> pd.DataFrame:
    """
    This function takes a selenium webdriver and a string of url,
    to return a pandas dataframe containing all market data, including loaded data from every tab.

    Precondition:   driver has been initialized and url is valid 
    Return:         a pandas dataframe containing full market data
    """
    driver.get(url)
    click_load_more(driver)
    notice_data_loaded()

    df_list = []
    for tab_name in tab_list:
        click_tab(driver, tab_name)
        html = driver.page_source
        soup = bs(html, "html.parser")
        headers = get_data_headers(soup)
        df = extract_dataframe(soup, headers)
        df_list.append(df)
        time.sleep(3)
        print(Fore.WHITE, f"- Extracted dataframe for {tab_name}.")

    df = pd.concat(df_list, axis=1)
    notice_data_extracted()
    return df


def clean_all(df:pd.DataFrame, currency:str) -> pd.DataFrame:
    """
    This function takes a pandas dataframe and the corresponding currency symbol,
    to return a pandas dataframe of formatted data.
    
    Precondition:   currency is a valid currency symbol: " USD", " CAD", etc.
    Return:         a pandas dataframe containing formatted market data
    """
    df = df.map(lambda x: str(x))
    df = df_remove_duplicate(df)
    df = df_fill_empty_cells(df)
    df = df_substitute_minus(df)

    df = df_remove_currency(df, currency)
    df = df_transform_number(df)
    return df
