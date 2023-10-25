# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

from trade_scan_libraries import sys
from trade_scan_libraries import tkinter as tk
from trade_scan_libraries import threading as td
from trade_scan_libraries import config_create, config_read_check, config_read_path, config_save
from trade_scan_functions import us_market_info, ca_market_info, zh_market_info, hk_market_info
from trade_scan_functions import main1, main2
from webdrivers.webdriver_initializer import start_webdriver, quit_webdriver

config_create()


def execute():
    driver = start_webdriver()
    config_save(accept1.get(), accept2.get(), accept3.get(), accept4.get(), accept5.get(),
                text1.get(), text2.get(), text3.get(), text4.get(), text5.get())
    if accept1.get() == "Accepted": main1(driver, text1.get(), us_market_info)
    if accept2.get() == "Accepted": main1(driver, text2.get(), ca_market_info)
    if accept3.get() == "Accepted": main1(driver, text3.get(), zh_market_info)
    if accept4.get() == "Accepted": main1(driver, text4.get(), hk_market_info)
    if accept5.get() == "Accepted": main2(driver, text5.get())
    quit_webdriver(driver)


def thread_execute():
    thread = td.Thread(target=execute) 
    thread.start()


# %% Initialize Window
root = tk.Tk()
root.title("TradeScan v1.1")
root.geometry("480x400")
root.iconbitmap("trade_scan_icon.ico")
root.resizable(width=False, height=False)

window = tk.Frame(root)
window.pack(expand=True)


# %% Creating Main Frames
frame1 = tk.LabelFrame(window, text="Extraction Options")
frame2 = tk.LabelFrame(window, text="Save Locations")
button1 = tk.Button(window, text="Execute", command=thread_execute)
button2 = tk.Button(window, text="Exit", command=sys.exit)

frame1.grid(row=1, column=0, sticky="nswe", padx=20, pady=10, columnspan=2)
frame2.grid(row=2, column=0, sticky="nswe", padx=20, pady=10, columnspan=2)
frame2.columnconfigure(1, weight=1)
button1.grid(row=3, column=0, sticky="nswe", padx=20, pady=10)
button2.grid(row=3, column=1, sticky="nswe", padx=20, pady=10)


# %% Defining Functionality - Checkbox
accept1 = tk.StringVar(value=config_read_check("check_us"))
accept2 = tk.StringVar(value=config_read_check("check_ca"))
accept3 = tk.StringVar(value=config_read_check("check_zh"))
accept4 = tk.StringVar(value=config_read_check("check_hk"))
accept5 = tk.StringVar(value=config_read_check("check_crypto"))

check1 = tk.Checkbutton(frame1, text="USA Stock Market",
                        variable=accept1, onvalue="Accepted", offvalue="Not Accepted")
check2 = tk.Checkbutton(frame1, text="Canadian Stock Market",
                        variable=accept2, onvalue="Accepted", offvalue="Not Accepted")
check3 = tk.Checkbutton(frame1, text="Chinese Stock Market",
                        variable=accept3, onvalue="Accepted", offvalue="Not Accepted")
check4 = tk.Checkbutton(frame1, text="Hong Kong Stock Market",
                        variable=accept4, onvalue="Accepted", offvalue="Not Accepted")
check5 = tk.Checkbutton(frame1, text="Cryptocurrency Market",
                        variable=accept5, onvalue="Accepted", offvalue="Not Accepted")

check1.grid(row=0, column=0, sticky="w")
check2.grid(row=1, column=0, sticky="w")
check3.grid(row=2, column=0, sticky="w")
check4.grid(row=3, column=0, sticky="w")
check5.grid(row=4, column=0, sticky="w")


# %% Defining Functionality - Save Location
path1 = tk.StringVar(value=config_read_path("output_path_us")[0])
path2 = tk.StringVar(value=config_read_path("output_path_ca")[0])
path3 = tk.StringVar(value=config_read_path("output_path_zh")[0])
path4 = tk.StringVar(value=config_read_path("output_path_hk")[0])
path5 = tk.StringVar(value=config_read_path("output_path_crypto")[0])

label1 = tk.Label(frame2, text="Stock (USA)")
label2 = tk.Label(frame2, text="Stock (Canada)")
label3 = tk.Label(frame2, text="Stock (China)")
label4 = tk.Label(frame2, text="Stock (Hong Kong)  ")
label5 = tk.Label(frame2, text="Cryptocurrency")
text1 = tk.Entry(frame2, textvariable=path1, width=30)
text2 = tk.Entry(frame2, textvariable=path2, width=30)
text3 = tk.Entry(frame2, textvariable=path3, width=30)
text4 = tk.Entry(frame2, textvariable=path4, width=30)
text5 = tk.Entry(frame2, textvariable=path5, width=30)

label1.grid(row=0, column=0, sticky="w")
label2.grid(row=1, column=0, sticky="w")
label3.grid(row=2, column=0, sticky="w")
label4.grid(row=3, column=0, sticky="w")
label5.grid(row=4, column=0, sticky="w")
text1.grid(row=0, column=1, sticky="e")
text2.grid(row=1, column=1, sticky="e")
text3.grid(row=2, column=1, sticky="e")
text4.grid(row=3, column=1, sticky="e")
text5.grid(row=4, column=1, sticky="e")


# %% Launch User Interface
window.mainloop()

