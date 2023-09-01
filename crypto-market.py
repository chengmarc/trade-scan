# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
try:
    # Import standard libraries
    import os, time, datetime, configparser

    # Import core libraries
    import pandas as pd
    from bs4 import BeautifulSoup as bs
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "All libraries imported.")

except:
    print("Dependencies missing, please use pip/conda to install all dependencies.")
    print("Standard libraries:      os, time, datetime, configparser")
    print("Core libraries:          pandas, bs4, selenium, colorama")
    input('Press any key to quit.')
    exit()
    
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

# %% Initialize web driver
options = Options()
options.add_argument("-headless")
service = Service(script_path + "\geckodriver.exe")

try:
    driver = webdriver.Firefox(service=service, options=options)
    driver.get("https://www.tradingview.com/markets/cryptocurrencies/prices-all/")
    print(Fore.GREEN + "Web driver initialized.")

except:
    print(Fore.RED + "Firefox Browser missing, please install Firefox Browser.")
    input('Press any key to quit.')
    exit()

# %% Click the "Load More" button until everything is loaded
timeout_times = 0
while True:
    try:
        driver.implicitly_wait(3)   # Wait for up to 5 seconds for the button to be clickable
        driver.find_element(By.CLASS_NAME, "loadButton-SFwfC2e0").click()
        print(Fore.WHITE + "Loading information...")
    except:
        timeout_times += 1
        if timeout_times > 5:   # After repeated timeout we conclude that everything has been loaded
            print(Fore.GREEN + "All information has been loaded.")
            break
        else: continue
del timeout_times

# %% Parse HTML
html = driver.page_source
soup = bs(html, "html.parser")
driver.quit()

df_raw = soup.find_all("tr", class_="row-RdUXZpkv listRow")
df_clean = pd.DataFrame(columns = ['Symbol', 'Name', 'Rank', 'Price', 'Change24h',
                                   'MarketCap', 'Volume24h', 'Supply', 'Category'])

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
        
    cell_right = row.find('td', class_='cell-RLhfr_y4 left-RLhfr_y4')
    row_content.append(cell_right.get_text())
    
    df_clean.loc[len(df_clean)] = row_content
    del cell_left, cell_mid, cells_mid, cell_right, row_content
    
print(Fore.WHITE + "Successfully extracted market data.")
    
# %% Data cleaning
df_trim = df_clean.copy()
df_trim = df_trim.replace("—", "N/A")

# Remove USD currency symbol
df_trim['Price'] = df_trim['Price'].str[:-4]
df_trim['MarketCap'] = df_trim['MarketCap'].str[:-4]
df_trim['Volume24h'] = df_trim['Volume24h'].str[:-4]
df_trim['Change24h'] = df_trim['Change24h'].str.replace("−", "-")

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
df_trim = str_to_float(df_trim, "MarketCap")
df_trim = str_to_float(df_trim, "Volume24h")
df_trim = str_to_float(df_trim, "Supply")

print(Fore.WHITE + "Data cleaning completed.")

# %% Export data to desired location
config = configparser.ConfigParser()
config.read('trade-scan config.ini')
output_path = config.get('Paths', 'output_path')

current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
output_name = "crypto-market-" + formatted_datetime + ".csv"

df_trim.to_csv(output_path + "\\" + output_name)

print("")
print(Fore.GREEN + "Data has been saved to desired location.")
print(Fore.WHITE + "Quitting automatically after 5 seconds.")

time.sleep(5)
