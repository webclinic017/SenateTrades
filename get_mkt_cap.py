# ticker --> market cap 

import pandas as pd 
from requests_html import HTMLSession
import os
import requests
from lxml import html 
import csv
from datetime import date,datetime
import re 
from bs4 import BeautifulSoup

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

