# Introduction
**trade-scan** is a web crawler that extract data from the famous analysis platform TradingView (a site that hosts up-to-date data on stock markets). **trade-scan** will help you download all the data into **.csv** format and store it locally, so that you can perform quantitative analysis using your favourite data science tools.

# First time use
1. Make sure you have the latest version of Google Chrome or Mozilla Firefox. 
2. Install **Python 3.10.11** on your computer. \
(note: should also work with other versions of Python, but not tested)

3. Download this repository as a **.zip** file and extract it.
4. Double click **trade-scan.bat** and data will be extracted automatically. \
(note: virtual environment will be created under "core-process" so it won't mess up with your existing environment)

# For further use
It is recommended to execute **trade-scan.bat** daily or weekly. This will takes around *15 minutes* and extract a daily snapshot of the stock market. This batch file executes **trade_scan_main.py** in "<ins>core-process</ins>".

# Save location
By default, data are saved under "<ins>market-data</ins>". \
If you want to change the output location, please edit in **config.ini**
