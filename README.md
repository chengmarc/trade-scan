# Introduction
**Notice: 1.22 is the last version of TradeScan, support for this application has ended.**

**trade-scan** is a web crawler that extract data from the famous analysis platform TradingView (a site that hosts up-to-date data on stock markets). **trade-scan** will help you download all the data into **.csv** format and store it locally, so that you can perform quantitative analysis using your favourite data science tools.

# Pre-requisite
Make sure you have the latest version of **Mozilla Firefox**. \
Support for **Google Chrome** has ended.

# First time use

Go to **Releases** on the right of this page, and download the **.exe** file. That's it.

If you have Python installed, you can also: 
1. Download this repository as a **.zip** file and extract it.
2. Double click **trade-scan.bat** and launch the application. \
(note: virtual environment will be created under "core-process" so it won't mess up with your existing environment)

# For further use
It is recommended to execute **trade-scan.bat** daily or weekly. It takes around *5 minutes* to extract a daily snapshot of each market.

# Save location
By default, data are saved under "<ins>C:\Users\Public\Documents</ins>" \
If you want to change the output location, please edit in **config.ini** under "<ins>C:\Users\Public</ins>".
