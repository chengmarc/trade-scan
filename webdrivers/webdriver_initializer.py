# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os, sys, getpass, warnings
script_path = os.path.dirname(os.path.realpath(__file__))

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "Webdriver initializer imported.")

except ImportError as e:
    print(f"The module '{e.name}' is not found, please install it using either pip or conda.")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()
    
# %% Functions for intializing webdrivers (Note: selenium and webdrivers are deprecated, requests is used instead.)


def initialize_firefox():
    # Current webdriver version:
    # mozilla/geckodriver 0.33.0
    options = FirefoxOptions()
    options.add_argument("-headless")
    service = FirefoxService(executable_path=os.path.join(script_path, "geckodriver.exe"))
    driver = webdriver.Firefox(service=service, options=options)
    return driver


def initialize_chrome():
    # Current webdriver version:
    # ChromeDriver 116.0.5845.96 (r1160321)
    options = ChromeOptions()
    options.add_argument("--headless")
    service = ChromeService(executable_path=os.path.join(script_path, "chromedriver.exe"))
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def error_browser():
    print("")
    print(Fore.WHITE + "If you already have Chrome or Firefox installed, but still see this message,",
                       "please check \"troubleshooting\" section on https://github.com/chengmarc/trade-scan.")  
    print("")
    getpass.getpass("Press Enter to quit in a few seconds...")
    sys.exit()


# %% Initialize webdriver (Note: selenium and webdrivers are deprecated, requests is used instead.)
warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    driver = initialize_firefox()
    print(Fore.GREEN + "Mozilla driver initialized.")
except:
    print(Fore.YELLOW + "Firefox not detected, attempt to proceed with Chrome...")

    try:
        driver = initialize_chrome()
        print(Fore.GREEN + "Chrome driver initialized.")
    except:
        print(Fore.RED + "Chrome not detected, aborting execution...")
        error_browser()
