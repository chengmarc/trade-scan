# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os, sys, time, datetime, configparser, getpass, threading
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

try:
    import tkinter
    import pandas as pd
    from bs4 import BeautifulSoup as bs
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "Core modules imported.")

except ImportError as e:
    print(f"The module '{e.name}' is not found, please install it using either pip or conda.")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()

from webdrivers.webdriver_initializer import By


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
│   └───extract_dataframe()         # dataframe extraction
│
├───extract_crypto()                # core function for extraction
│   │
│   ├───click_load_more()           # dynamic interaction (load more)
│   │
│   └───extract_df_crypto()         # dataframe extraction
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
├───config_create()                 # detect config and create one if not exist
├───config_read_check()             # read from section [Checks] in config
├───config_read_path()              # read from section [Paths] in config
├───config_save()                   # save to config
│
├───get_date()                      # get current date
└───get_datetime()                  # get current datetime
"""


# %% Pre-defined tab list
tab_list = ["overview", "performance", "valuation", "dividends", "profitability",
            "incomeStatement", "balanceSheet", "cashFlow", "technicals"]


# %% Functions for web interactions


def click_load_more(driver) -> None:
    """
    The function takes a selenium webdriver and click the "load" button until everything is loaded.

    Precondition:   selenium webdriver has opened a TradingView market page
    """
    timeout_times = 0
    while True:
        try:
            # Wait for up to 3 seconds for the button to be clickable
            driver.implicitly_wait(3)
            driver.find_element(By.CLASS_NAME, "button-SFwfC2e0").click()
            info_loading()

        except:
            # After repeated timeout we conclude that everything has been loaded
            timeout_times += 1
            if (timeout_times > 10): 
                info_data_loaded()
                break
            else: continue


def click_tab(driver, tab_name: str) -> None:
    """
    The function takes a selenium webdriver and click the tab given.

    Precondition:   selenium webdriver has opened a TradingView market page
                    tab name is a valid id that represents a clickable object
    """
    button = driver.find_element(By.ID , tab_name)
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


def extract_df_crypto(soup) -> pd.DataFrame:
    """
    The function takes a BeautifulSoup object to return a pandas dataframe.

    Precondition:   soup has been correctly parsed from crypto market url
    Return:         a pandas dataframe containing the market data
    """
    df = pd.DataFrame(columns = ['Symbol', 'Name', 'Rank', 'Price', 'Change24h',
                                 'MarketCap', 'Volume24h', 'Supply', 'Category'])
    trow = soup.find_all("tr", class_="row-RdUXZpkv listRow")
    for row in trow:
        row_content = []

        cell_left = row.find('td', class_='cell-RLhfr_y4 left-RLhfr_y4 cell-fixed-ZtyEm8a1 onscroll-shadow')
        symbol = cell_left.find('a', class_='apply-common-tooltip tickerNameBox-GrtoTeat tickerName-GrtoTeat')
        name = cell_left.find('sup', class_='apply-common-tooltip tickerDescription-GrtoTeat')
        row_content.append(symbol.get_text())
        row_content.append(name.get_text())

        cells_mid = row.find_all('td', class_='cell-RLhfr_y4 right-RLhfr_y4')
        for cell_mid in cells_mid:
            row_content.append(cell_mid.get_text())

        cell_right = row.find('td', class_='cell-RLhfr_y4 left-RLhfr_y4')
        row_content.append(cell_right.get_text())

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
    
    info_remove_duplicate()
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
    
    info_fill_empty_cells()
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

    info_substitute_minus()
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

    info_remove_currency()
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


def cell_str_to_float(string: str) -> float:
    """
    The function takes a number abbreviation string and returns the number.

    Precondition:   string contains an abbreviated number: "10K", "20M", "30B", "40T"
    Return:         a float number such as 10000

    #Example
    input:  "768M"
    output: "768000000.00"
    """
    if string[-2:] in get_abbrev_list(["K","M","B","T"]):
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

    info_transform_number()
    return df


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

    df_list = []
    for tab_name in tab_list:
        click_tab(driver, tab_name)
        html = driver.page_source
        soup = bs(html, "html.parser")
        headers = get_data_headers(soup)
        df = extract_dataframe(soup, headers)
        df_list.append(df)
        info_extracting(tab_name)
    df = pd.concat(df_list, axis=1)

    return df


def extract_crypto(driver) -> pd.DataFrame():
    """
    This function takes a selenium webdriver to return a pandas dataframe containing crypto market data.

    Precondition:   driver has been initialized
    Return:         a pandas dataframe containing crypto market data
    """
    driver.get("https://www.tradingview.com/markets/cryptocurrencies/prices-all/")
    click_load_more(driver)
    
    html = driver.page_source
    soup = bs(html, "html.parser")
    df = extract_df_crypto(soup)

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


# %% Function for output path and output time


def config_create() -> None:
    """
    This function detects if the config file exist.
    If not, it will create the config file with default save locations.
    """
    config_file = r"C:\Users\Public\config_trade_scan.ini"
    if not os.path.exists(config_file):
        content = ("[Checks]\n"
                   "check_us=Accepted\n"
                   "check_ca=Accepted\n"
                   "check_zh=Accepted\n"
                   "check_hk=Accepted\n"
                   "check_crypto=Not Accepted\n"
                   "[Paths]\n"
                   r"output_path_us=C:\Users\Public\Documents" + "\n"
                   r"output_path_ca=C:\Users\Public\Documents" + "\n"
                   r"output_path_zh=C:\Users\Public\Documents" + "\n"
                   r"output_path_hk=C:\Users\Public\Documents" + "\n"
                   r"output_path_crypto=C:\Users\Public\Documents" + "\n")
        with open(config_file, "w") as f:
            f.write(content)
            f.close()


def config_read_check(selection: str) -> str:
    """
    Given a selection, this function will return the corresponding path.

    Return:         a string that represents either checked or not checked
    """
    config_file = r"C:\Users\Public\config_trade_scan.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    config_check = config.get("Checks", selection)
    return config_check


def config_read_path(selection: str) -> (str, bool):
    """
    Given a selection, this function will return the corresponding path.

    Return:         a tuple of str and boolean
                    the string represents the path
                    the boolean represents the validity of the path
    """
    config_file = r"C:\Users\Public\config_trade_scan.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    config_path = config.get("Paths", selection)

    if os.path.isdir(config_path):
        return config_path, True
    else:
        return config_path, False


def config_save(check1, check2, check3, check4, check5,
                path1, path2, path3, path4, path5) -> None:
    """
    Given ten strings, this function will save the strings to the config file.
    """
    config_file = r"C:\Users\Public\config_trade_scan.ini"
    content = ("[Checks]\n"
               f"check_us={check1}\n"
               f"check_ca={check2}\n"
               f"check_zh={check3}\n"
               f"check_hk={check4}\n"
               f"check_crypto={check5}\n"
               "[Paths]\n"
               f"output_path_us={path1}\n"
               f"output_path_ca={path2}\n"
               f"output_path_zh={path3}\n"
               f"output_path_hk={path4}\n"
               f"output_path_crypto={path5}\n")
    with open(config_file, "w") as f:
        f.write(content)
        f.close()


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
    print("")


def notice_save_success(filename: str) -> None:
    print(Fore.WHITE + "Successfully loaded output config.")
    print(Fore.WHITE + f"{filename} has been saved to the desired location.")
    print("")


def info_loading() -> None:
    print(Fore.WHITE + "INFO: Loading information...")


def info_data_loaded() -> None:
    print(Fore.GREEN + "INFO: All data loaded.")
    print("")


def info_extracting(tab_name):
    print(Fore.WHITE + f"INFO: Extracted dataframe for {tab_name}.")


def info_data_extracted() -> None:
    print(Fore.GREEN + "INFO: All data extracted.")
    print("")


def info_remove_duplicate():
    print(Fore.WHITE + "INFO: Removed duplicated columns.")


def info_fill_empty_cells():
    print(Fore.WHITE + "INFO: Filled up empty cells.")


def info_substitute_minus():
    print(Fore.WHITE + "INFO: Replaced U+2212 with U+002D.")


def info_remove_currency():
    print(Fore.WHITE + "INFO: Removed currency symbol.")


def info_transform_number():
    print(Fore.WHITE + "INFO: Transformed abbreviations to numbers.")


def info_data_cleaned() -> None:
    print(Fore.GREEN + "INFO: Data Cleaning complete.")
    print("")


def error_save_failed(filename: str) -> None:
    print("")
    print(Fore.RED + f"Failed to save {filename}")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()

