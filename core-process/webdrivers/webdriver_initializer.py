# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os, sys, getpass, warnings, subprocess
script_path = os.path.dirname(os.path.realpath(__file__))

try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver import Firefox, Chrome
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    print("DRIVER: Webdriver initializer imported.")

except ImportError as e:
    print(f"DRIVER: The module '{e.name}' is not found, please install it using either pip or conda.")
    getpass.getpass("DRIVER: Press Enter to quit in a few seconds...")
    sys.exit()


# %% Function overview
"""
The graph below is an overview of the call structure of the functions.
│ 
├───start_webdriver()               # attempt to intialize a webdriver
│   │
│   ├───initialize_firefox()        # firefox initializer
│   ├───initialize_chrome()         # chrome initializer
│   └───error_browser()             # user notice
│
└───quit_webdriver()                # quit the given webdriver
"""


# %% Functions for intializing webdrivers


def initialize_firefox(bit: int) -> Firefox:
    # Current webdriver version:
    # mozilla/geckodriver 0.33.0

    options = FirefoxOptions()
    options.add_argument("-headless")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    service = FirefoxService()
    service.creation_flags = subprocess.CREATE_NO_WINDOW

    if bit == 32:
        binary = os.path.join(script_path, "geckodriver32.exe")
        driver = Firefox(executable_path=binary, service=service, options=options)
    if bit == 64:
        binary = os.path.join(script_path, "geckodriver64.exe")
        driver = Firefox(executable_path=binary, service=service, options=options)
    return driver


def initialize_chrome() -> Chrome:
    # Current webdriver version:
    # ChromeDriver 119.0.6045.105 (r1204232)

    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    service = ChromeService()
    service.creation_flags = subprocess.CREATE_NO_WINDOW
    
    binary = os.path.join(script_path, "chromedriver.exe")
    driver = Chrome(executable_path=binary, service=service, options=options)
    return driver


def error_browser():
    print("TradeScan currently support:\n" +
          "\n" +
          " - Mozilla Firefox (Latest) 32-bit\n" +
          " - Mozilla Firefox (Latest) 64-bit\n" +
          " - Google Chrome (Version 118) 64-bit\n" +
          "\n" +
          "Google Chrome updates very frequently, and old version of chromedriver " +
          "is typically not compatiable with newer versions of Google Chrome, " +
          "while old version of geckodriver is usually compatiable with newer versions of Mozilla Firefox. \n" +
          "\n" +
          "If you are seeing this issue, it is recommended to download the latest version of Mozilla Firefox and try again.")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()


# %% Core functions


def start_webdriver():
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    try:
        driver = initialize_firefox(64)
        print("DRIVER: Mozilla Firefox (64-bit) initialized.")
    except:
        print("DRIVER: Mozilla Firefox (64-bit) not detected, attempt to proceed with Mozilla Firefox (32-bit)...")

        try:
            driver = initialize_firefox(32)
            print("DRIVER: Mozilla Firefox (32-bit) initialized.")
        except:
            print("DRIVER: Mozilla Firefox (32-bit) not detected, attempt to proceed with Google Chrome (64-bit)...")

            try:
                driver = initialize_chrome()
                print("DRIVER: Google Chrome (64-bit) initialized.")
            except:
                print("DRIVER: Google Chrome (64-bit) not detected, aborting execution...")
                error_browser()

    print("")
    return driver

def quit_webdriver(driver):
    
    driver.quit()
    print("DRIVER: Webdriver successfully closed.")
    print("")

