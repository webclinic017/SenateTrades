# ticker --> market cap 
# add more helper methods for screening
import pandas as pd 
from requests_html import HTMLSession
import os
import requests
from lxml import html 
import csv
from datetime import date,datetime
import re 
from bs4 import BeautifulSoup
import nums_from_string

def fetchSession(url):
    session = HTMLSession()
    r = session.get(url)
    return r

def getHTML(url):
    r = fetchSession(url)
    h = r.text
    doc = BeautifulSoup(h, 'html.parser')
    return doc

def parseToMillions(value_string):
    unit = value_string[-1:]
    number = float(value_string[:-1])
    #keep in units of millions
    if unit == 'B':
        number = number * 1000
    elif unit == 'T':
        number = number * 1000000
    return number

def arr_to_dict(lst):
    it = iter(lst)
    res_dict = dict(zip(it,it))
    return res_dict 

def value_to_ints(value):
    bad_chars = [
        ',','$','-'
    ]
    for c in bad_chars:
        value = value.replace(c,'')
    low, high = [
        int(x) for x in (value.split('  ', 1))
    ]
    return [low,high]

def determineLargeTrades(all_trades, date_dt):
    large_trades = []
    # refine parameters. condsider buy/sell cases?
    for t in all_trades:
        if t['value'][1] > 50001 and t['trade type'] == 'Purchase':
            # clean up data for presenation
            trade_date = str(t['trade date']) + ' (' + str((
                date_dt - datetime.strptime(
                    t['trade date'], '%Y-%m-%d'
                ).date()
            )).split(',')[0] + ' ago)'

            value_string = '$' + (
                "{:,}".format(t['value'][0])
            ) + ' to $' + (
                "{:,}".format(t['value'][1])
            )
            large_trades.append(
                 {
                'trade' : t['trade'],
                'trade type' : t['trade type'],
                'value' : value_string,
                'trade date' : trade_date,
                'senator' : t['senator']
                }
            )
    return large_trades

def getMktCap(ticker):
    url = 'https://finance.yahoo.com/quote/{}/'.format(ticker)
    soup = getHTML(url)
    quote_summary = soup.find(id='quote-summary')
    if quote_summary is None:
        return -1
    tables = quote_summary.find_all('table')
    if len(tables) == 0:
        return -1
    mc_table = tables[1]
    mc_rows = mc_table.find_all('td')
    mc_string = str(mc_rows[1])
    value = re.search('>(.*)<', mc_string).group(1)
    if value == 'N/A':
        return -1
    return round(parseToMillions(value),2)

today = '2022-04-13'
today_dt = datetime.strptime(
    today, '%Y-%m-%d'
).date()

def isLarge(value_):
    return value_[1] > 50001
# ignores ETFs
def isEquity(trade_):
    regex = re.findall('\[(.*?)\]', trade_)
    return (
        len(regex) != 0 and 'Common Stock' in trade_
    )
def isPurchase(trade_type_):
    return trade_type_ == 'Purchase'

def isLEP(t):
    return (
        isLarge(t['value']) and isPurchase(t['trade type']) and isEquity(t['trade'])
    )

def getLargeEquity(all_trades):
    large_trades = []
    for t in all_trades:
        if isLEP(t):
            # clean up data for presenation
            # removed part to find how many days ago for simplicity for testing
            trade_date = t['trade date']
            value_string = '$' + (
                "{:,}".format(t['value'][0])
            ) + ' to $' + (
                "{:,}".format(t['value'][1])
            )
            large_trades.append(
                    {
                'trade' : t['trade'],
                'trade type' : t['trade type'],
                'value' : value_string,
                'trade date' : trade_date,
                'senator' : t['senator']
                }
            )
    return large_trades

def getTicker(trade_):
    return re.findall('\[(.*?)\]', trade_)[0]

def list_tickers(equity_trades):
    tickers = []
    for e in equity_trades:
        tickers.append(
            getTicker(e['trade'])
        )
    return tickers

def isSmallCap(ticker):
    # returns -1 when error in finding mkt cap
    return getMktCap(ticker) < 2000 and getMktCap(ticker) > 0

def isSCEP(t):
    if isEquity(t['trade']):
        return (
            isSmallCap(getTicker(t['trade'])) and isPurchase(t['trade type'])
        )

def getSmallCaps(all_trades):
    large_trades = []
    for t in all_trades:
        if isSCEP(t):
            # clean up data for presenation
            # removed part to find how many days ago for simplicity for testing
            trade_date = t['trade date']
            value_string = '$' + (
                "{:,}".format(t['value'][0])
            ) + ' to $' + (
                "{:,}".format(t['value'][1])
            )
            large_trades.append(
                 {
                'trade' : t['trade'],
                'trade type' : t['trade type'],
                'value' : value_string,
                'trade date' : trade_date,
                'senator' : t['senator']
                }
            )
    return large_trades

# fix 
def getImportantEquity(all_trades):
    important_trades = []
    for t in all_trades:
        if isEquity(t['trade']) and isPurchase(t['trade']):
            print('1')
            if isLarge(t['trade']):
                print('2')
                important_trades.append(t)
            elif isSmallCap(getTicker(t['trade'])):
                print('3')
                important_trades.append(t)
    return important_trades