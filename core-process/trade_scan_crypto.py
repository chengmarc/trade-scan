# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

import trade_scan_libraries as tsl

# %% Load data
driver = tsl.driver
driver.get("https://www.tradingview.com/markets/cryptocurrencies/prices-all/")
tsl.click_load_more(driver)
print("")
print(tsl.Fore.GREEN + "All data loaded.")
print("")

# %% Parse HTML
html = driver.page_source
soup = tsl.bs(html, "html.parser")
driver.quit()

df_raw = soup.find_all("tr", class_="row-RdUXZpkv listRow")
df_clean = tsl.pd.DataFrame(columns = ['Symbol', 'Name', 'Rank', 'Price', 'Change24h',
                                   'MarketCap', 'Volume24h', 'Supply', 'Category'])

print(tsl.Fore.WHITE + "Successfully parsed html content.")

# %% Extract data
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

print(tsl.Fore.WHITE + "Successfully extracted market data.")

# %% Clean data
df = df_clean.copy()
df = tsl.df_fill_empty_cells(df)
df = tsl.df_substitute_minus(df)

currency_list = ["Price", "MarketCap", "Volume24h", "Change24h"]
substitue_list = ["MarketCap", "Volume24h", "Supply"]

df = tsl.col_remove_currency(df, currency_list, " USD")
df = tsl.col_transform_number(df, substitue_list)

# %% Export data
try:
    output_path, valid = tsl.get_and_check_config("output_path_crypto", os.path.dirname(script_path))
    output_name = f"crypto-market-{tsl.get_datetime()}.csv"
    df.to_csv(os.path.join(output_path, output_name))
    if valid:
        tsl.notice_save_desired(output_name)
    else:
        tsl.notice_save_default(output_name)
except:
    tsl.error_save_failed(output_name)
    
tsl.sys.exit()
