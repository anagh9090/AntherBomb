#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import shutil
import sys
import subprocess
import string
import random
import json
import re
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.decorators import MessageDecorator
from utils.provider import APIProvider

try:
    import requests
    from colorama import Fore, Style
except ImportError:
    print("\tSome dependencies could not be imported (possibly not installed)")
    print("Type `pip3 install -r requirements.txt` to install all required packages")
    sys.exit(1)

# Constants & Configuration
__VERSION__ = "1.0-local"
__CONTRIBUTORS__ = ['anagh9090']
ALL_COLORS = [Fore.GREEN, Fore.RED, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
RESET_ALL = Style.RESET_ALL
ASCII_MODE = False

def readisdc():
    with open("isdcodes.json") as file:
        isdcodes = json.load(file)
    return isdcodes

def clr():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def bann_text():
    clr()
    # Added r prefix to solve SyntaxWarning: invalid escape sequence
    logo = r"""
          _____          __  .__                __________              ___.
   /  _  \   _____/  |_|  |__   __________\______   \ ____   _____\_ |__
  /  /_\  \ /    \    __\  |  \_/ __ \_  __ \    |  _//  _ \ /     \| __ \
 /    |    \    |  \  | |   Y  \  ___/|  | \/    |   (  <_> )  Y Y  \ \_\ \
 \____|__  /___|  /__| |___|  /\___  >__|     |______  /\____/|__|_|  /___  /
         \/     \/          \/     \/                \/              \/    \/
"""
    if ASCII_MODE:
        logo = ""
    version = "Version: " + __VERSION__
    contributors = "Contributors: " + " ".join(__CONTRIBUTORS__)
    print(random.choice(ALL_COLORS) + logo + RESET_ALL)
    mesgdcrt.SuccessMessage(version)
    mesgdcrt.SectionMessage(contributors)
    print()

def check_intr():
    try:
        requests.get("https://motherfuckingwebsite.com", timeout=5)
    except Exception:
        bann_text()
        mesgdcrt.FailureMessage("Poor internet connection detected")
        sys.exit(2)

def format_phone(num):
    num = [n for n in num if n in string.digits]
    return ''.join(num).strip()

def get_phone_info():
    while True:
        cc = input(mesgdcrt.CommandMessage("Enter your country code (Without +): "))
        cc = format_phone(cc)
        if not country_codes.get(cc, False):
            mesgdcrt.WarningMessage("The country code ({cc}) is invalid or unsupported".format(cc=cc))
            continue
        target = input(mesgdcrt.CommandMessage("Enter the target number: +" + cc + " "))
        target = format_phone(target)
        if ((len(target) <= 6) or (len(target) >= 12)):
            mesgdcrt.WarningMessage("The phone number ({target}) is invalid".format(target=target))
            continue
        return (cc, target)

def get_mail_info():
    mail_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    while True:
        target = input(mesgdcrt.CommandMessage("Enter target mail: "))
        if not re.search(mail_regex, target, re.IGNORECASE):
            mesgdcrt.WarningMessage("The mail ({target}) is invalid".format(target=target))
            continue
        return target

def pretty_print(cc, target, success, failed):
    requested = success + failed
    mesgdcrt.SectionMessage("Bombing is in progress - Please be patient")
    mesgdcrt.GeneralMessage("Target       : " + cc + " " + target)
    mesgdcrt.GeneralMessage("Sent         : " + str(requested))
    mesgdcrt.GeneralMessage("Successful   : " + str(success))
    mesgdcrt.GeneralMessage("Failed       : " + str(failed))
    mesgdcrt.WarningMessage("This tool was made for research purposes only")

def workernode(mode, cc, target, count, delay, max_threads):
    api = APIProvider(cc, target, mode, delay=delay)
    clr()
    mesgdcrt.SectionMessage("Gearing up the Bomber")
    mesgdcrt.GeneralMessage("API Version   : " + api.api_version)
    mesgdcrt.GeneralMessage("Target        : " + cc + target)
    mesgdcrt.GeneralMessage("Amount        : " + str(count))
    mesgdcrt.GeneralMessage("Threads       : " + str(max_threads))
    print()
    input(mesgdcrt.CommandMessage("Press [ENTER] to start, [CTRL+C] to stop"))

    if len(APIProvider.api_providers) == 0:
        mesgdcrt.FailureMessage("Target not supported")
        sys.exit()

    success, failed = 0, 0
    while success < count:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            jobs = [executor.submit(api.hit) for _ in range(count - success)]
            for job in as_completed(jobs):
                result = job.result()
                if result is None:
                    mesgdcrt.FailureMessage("Limit reached for this target")
                    sys.exit()
                if result:
                    success += 1
                else:
                    failed += 1
                clr()
                pretty_print(cc, target, success, failed)

    print("\n")
    mesgdcrt.SuccessMessage("Bombing completed!")
    time.sleep(1.5)
    sys.exit()

def selectnode(mode="sms"):
    mode = mode.lower().strip()
    try:
        clr()
        bann_text()
        check_intr()

        max_limit = {"sms": 500, "call": 15, "mail": 200}
        cc, target = "", ""
        if mode in ["sms", "call"]:
            cc, target = get_phone_info()
            if cc != "91":
                max_limit.update({"sms": 100})
        elif mode == "mail":
            target = get_mail_info()

        limit = max_limit[mode]
        while True:
            try:
                message = "Enter number of {type} (Max {limit}): ".format(type=mode.upper(), limit=limit)
                count = int(input(mesgdcrt.CommandMessage(message)).strip())
                if count > limit or count <= 0:
                    count = limit

                delay = float(input(mesgdcrt.CommandMessage("Enter delay (seconds): ")).strip())
                max_thread_limit = (count // 10) if (count // 10) > 0 else 1
                max_threads = int(input(mesgdcrt.CommandMessage("Threads (Rec: {m}): ".format(m=max_thread_limit))).strip())
                break
            except Exception:
                mesgdcrt.FailureMessage("Invalid Input!")

        workernode(mode, cc, target, count, delay, max_threads)
    except KeyboardInterrupt:
        sys.exit()

# Main Entry
mesgdcrt = MessageDecorator("icon")
try:
    country_codes = readisdc()["isdcodes"]
except Exception:
    print("Error: isdcodes.json is missing!")
    sys.exit(1)

parser = argparse.ArgumentParser(description="Friendly Spammer Application")
# Added double dashes to allow --sms, --call, etc.
parser.add_argument("--sms", action="store_true")
parser.add_argument("--call", action="store_true")
parser.add_argument("--mail", action="store_true")
parser.add_argument("--ascii", action="store_true")

if __name__ == "__main__":
    args = parser.parse_args()
    if args.ascii:
        ASCII_MODE = True

    if args.mail:
        selectnode(mode="mail")
    elif args.call:
        selectnode(mode="call")
    elif args.sms:
        selectnode(mode="sms")
    else:
        choice = ""
        avail = {"1": "SMS", "2": "CALL", "3": "MAIL"}
        while choice not in avail:
            clr()
            bann_text()
            for k, v in avail.items():
                print("[ {k} ] {v} BOMB".format(k=k, v=v))
            choice = input(mesgdcrt.CommandMessage("Enter Choice : "))
        selectnode(mode=avail[choice].lower())
