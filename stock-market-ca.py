# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
from colorama import init, Fore
init()

# %% Import selenium webdriver, set path for webdriver, connect to the selected page
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

url = "https://www.tradingview.com/markets/stocks-canada/market-movers-all-stocks/"

options = Options()
options.add_argument("-headless")

driver = webdriver.Firefox(options=options)
driver.get(url)

print(Fore.GREEN + "Web driver initialized.")

# %% Click the "Load More" button until everything is loaded
timeout_times = 0
while True:
    try:
        driver.implicitly_wait(3)   # Wait for up to 5 seconds for the button to be clickable
        driver.find_element(By.CLASS_NAME, "loadButton-SFwfC2e0").click()
        print(Fore.YELLOW + "Loading information...")
    except:
        timeout_times += 1
        if timeout_times > 5:   # After repeated timeout we conclude that everything has been loaded
            print(Fore.GREEN + "All information has been loaded.")
            break
        else: continue
del timeout_times

# %% Import beautiful soup for scraping, and pandas for data processing
import pandas as pd
from bs4 import BeautifulSoup as bs

html = driver.page_source
soup = bs(html, "html.parser")
driver.quit()

df_raw = soup.find_all("tr", class_="row-RdUXZpkv listRow")
df_clean = pd.DataFrame(columns = ['Symbol', 'Company', 'Price', 'Change%1D', 'Change1D',
                                   'Volume1D', 'Volume*Price1D', 'MarketCap', 'MarketCapPerformance%1Y',
                                   'PriceEarningRatio', 'EarningPerShare(TTM)', 'Employees(FY)', 'Sector'])

print(Fore.WHITE + "Successfully parsed html content.")

# %% Extract useful data, store in a clean data frame
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
    del cell_left, cell_mid, cells_mid, cell_right, cells_right, row_content
    
print(Fore.WHITE + "Successfully extracted market data.")
    
# %% Data cleaning
df_trim = df_clean.copy()
df_trim = df_trim.replace("—", "N/A")

# Remove USD currency symbol
df_trim['Price'] = df_trim['Price'].str[:-4]
df_trim['Change1D'] = df_trim['Change1D'].str[:-4]
df_trim['Volume*Price1D'] = df_trim['Volume*Price1D'].str[:-4]
df_trim['MarketCap'] = df_trim['MarketCap'].str[:-4]
df_trim['EarningPerShare(TTM)'] = df_trim['EarningPerShare(TTM)'].str[:-4]

# Replace "−" to "-"
df_trim['Change%1D'] = df_trim['Change%1D'].str.replace("−", "-")
df_trim['Change1D'] = df_trim['Change1D'].str.replace("−", "-")
df_trim['MarketCapPerformance%1Y'] = df_trim['MarketCapPerformance%1Y'].str.replace("−", "-")
df_trim['EarningPerShare(TTM)'] = df_trim['EarningPerShare(TTM)'].str.replace("−", "-")

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

# Change string to float for the dataframe
df_trim = str_to_float(df_trim, "Volume1D")
df_trim = str_to_float(df_trim, "Volume*Price1D")
df_trim = str_to_float(df_trim, "MarketCap")
df_trim = str_to_float(df_trim, "Employees(FY)")

print(Fore.WHITE + "Data cleaning completed.")

# %% Export data to desired location
import os
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

import configparser
config = configparser.ConfigParser()
config.read('trade-scan config.ini')
output_path = config.get('Paths', 'output_path')

from datetime import date
output_name = "stock-market-ca-" + date.today().strftime("%Y-%m-%d") + ".csv"

df_trim.to_csv(output_path + "\\" + output_name)

print("")
print(Fore.GREEN + "Data has been saved to desired location.")
print(Fore.WHITE + "Quitting automatically after 5 seconds.")

import time
time.sleep(5)
