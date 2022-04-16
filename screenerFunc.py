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

def getmktCap(ticker):
    url = 'https://finance.yahoo.com/quote/{}/'.format(ticker)
    soup = getHTML(url)
    quote_summary = soup.find(id='quote-summary')
    tables = quote_summary.find_all('table')
    mc_table = tables[1]
    mc_rows = mc_table.find_all('td')
    mc_string = str(mc_rows[1])
    value = re.search('>(.*)<', mc_string).group(1)
    return parseToMillions(value)

today = '2022-04-13'
today_dt = datetime.strptime(
    today, '%Y-%m-%d'
).date()

def scrapeAllTradesDate(date, trades):
    r = fetchSession('https://sec.report/Senate-Stock-Disclosures')
    n = len(trades)
    all_trades = []
    l1_head = [
        'trade date', 'file date', 'trade', 'senator'
    ]
    l2_head = [
        'trade type', 'value'
    ]
    current = True
    while current:
        for i in range(0,n,2):
            trade = []
            l1_elements = trades[i].find('td')
            l2_elements = trades[i+1].find('td')[:-1]
            file_date, trade_date = l1_elements[0].text.split('\n')
            trade_snip = l1_elements[1].text
            senator = l1_elements[2].text
            l1_cleaned = [
                trade_date,file_date,trade_snip,senator
            ]
            for h,e in zip(l1_head, l1_cleaned):
                trade.append(h)
                trade.append(e)
            for h,e in zip(l2_head, l2_elements):
                trade.append(h)
                trade.append(e.text)
            if trade[3] != date:
                current = False
                break 
            trade[9] = trade[9].split('\n', 1)[0]
            trade[11] = value_to_ints(trade[11])
            trade = arr_to_dict(trade)
            all_trades.append(trade)
    return all_trades

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
                'Trade' : t['trade'],
                'Trade Type' : t['trade type'],
                'Value' : value_string,
                'Trade Date' : trade_date,
                'Senator' : t['senator']
                }
            )
    return large_trades

def getTicker(trade_):
    return re.findall('\[(.*?)\]', trade_)[0]

def list_tickers(equity_trades):
    tickers = []
    for e in equity_trades:
        tickers.append(
            getTicker(e['Trade'])
        )
    return tickers

def isSmallCap(ticker):
    return getmktCap(ticker) < 2000

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
                'Trade' : t['trade'],
                'Trade Type' : t['trade type'],
                'Value' : value_string,
                'Trade Date' : trade_date,
                'Senator' : t['senator']
                }
            )
    return large_trades