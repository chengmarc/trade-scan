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


def thread():
    thread = td.Thread(target=execute) 
    thread.start()


def exit():
    root.destroy()
    sys.exit()


# %% Initialize Window
root = tk.Tk()
root.title("TradeScan v1.21")
root.iconbitmap("trade_scan_icon.ico")
root.resizable(width=False, height=False)

window = tk.Frame(root)
window.grid(padx=20, pady=10)


# %% Creating main frames
frame1 = tk.LabelFrame(window, text="Console")
frame2 = tk.LabelFrame(window, text="Extraction Options & Save Locations")

frame1.grid(row=1, column=0, sticky="nswe", padx=10, pady=10, columnspan=2)
frame2.grid(row=2, column=0, sticky="nswe", padx=10, pady=10, columnspan=2)


# %% Creating buttons
window.columnconfigure(0, weight=9)
window.columnconfigure(1, weight=10)

button1 = tk.Button(window, text="Execute", command=thread)
button2 = tk.Button(window, text="Exit", command=exit)

button1.grid(row=4, column=0, sticky="nswe", padx=10, pady=20, columnspan=1)
button2.grid(row=4, column=1, sticky="nswe", padx=10, pady=20, columnspan=1)


# %% Frame 1 content - console


class Console(tk.Text):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(state=tk.DISABLED)
        self.configure(background="black", foreground="white")
        self.configure(font=("Consolas", 10))
        self.configure(height=20, width=60)

    def flush(self):
        pass

    def write(self, text):
        self.configure(state=tk.NORMAL)
        self.insert(tk.END, text)
        self.see(tk.END)
        self.configure(state=tk.DISABLED)


console = Console(frame1)
console.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

sys.stdout = console


# %% Frame 2 content - options
frame2.columnconfigure(0, weight=1)
frame2.columnconfigure(1, weight=6)


def checkbox(frame):
    global accept1, accept2, accept3, accept4, accept5
    accept1 = tk.StringVar(value=config_read_check("check_us"))
    accept2 = tk.StringVar(value=config_read_check("check_ca"))
    accept3 = tk.StringVar(value=config_read_check("check_zh"))
    accept4 = tk.StringVar(value=config_read_check("check_hk"))
    accept5 = tk.StringVar(value=config_read_check("check_crypto"))

    global check1, check2, check3, check4, check5
    check1 = tk.Checkbutton(frame, text="USA Stock Market",
                            variable=accept1, onvalue="Accepted", offvalue="Not Accepted")
    check2 = tk.Checkbutton(frame, text="Canadian Stock Market",
                            variable=accept2, onvalue="Accepted", offvalue="Not Accepted")
    check3 = tk.Checkbutton(frame, text="Chinese Stock Market",
                            variable=accept3, onvalue="Accepted", offvalue="Not Accepted")
    check4 = tk.Checkbutton(frame, text="Hong Kong Stock Market",
                            variable=accept4, onvalue="Accepted", offvalue="Not Accepted")
    check5 = tk.Checkbutton(frame, text="Cryptocurrency Market",
                            variable=accept5, onvalue="Accepted", offvalue="Not Accepted")

    check1.grid(row=0, column=0, sticky="w", padx=5, pady=1)
    check2.grid(row=1, column=0, sticky="w", padx=5, pady=1)
    check3.grid(row=2, column=0, sticky="w", padx=5, pady=1)
    check4.grid(row=3, column=0, sticky="w", padx=5, pady=1)
    check5.grid(row=4, column=0, sticky="w", padx=5, pady=1)


def save_location(frame):
    global path1, path2, path3, path4, path5
    path1 = tk.StringVar(value=config_read_path("output_path_us")[0])
    path2 = tk.StringVar(value=config_read_path("output_path_ca")[0])
    path3 = tk.StringVar(value=config_read_path("output_path_zh")[0])
    path4 = tk.StringVar(value=config_read_path("output_path_hk")[0])
    path5 = tk.StringVar(value=config_read_path("output_path_crypto")[0])

    global text1, text2, text3, text4, text5
    text1 = tk.Entry(frame, textvariable=path1)
    text2 = tk.Entry(frame, textvariable=path2)
    text3 = tk.Entry(frame, textvariable=path3)
    text4 = tk.Entry(frame, textvariable=path4)
    text5 = tk.Entry(frame, textvariable=path5)
    
    text1.grid(row=0, column=1, sticky="we", padx=5, pady=1)
    text2.grid(row=1, column=1, sticky="we", padx=5, pady=1)
    text3.grid(row=2, column=1, sticky="we", padx=5, pady=1)
    text4.grid(row=3, column=1, sticky="we", padx=5, pady=1)
    text5.grid(row=4, column=1, sticky="we", padx=5, pady=1)


checkbox(frame2)
save_location(frame2)


# %% Launch user interface
root.mainloop()

