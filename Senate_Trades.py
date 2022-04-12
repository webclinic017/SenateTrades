# add variable for days since trade (filed - traded)

import pandas as pd 
from requests_html import HTMLSession
from lxml import html 
from datetime import date

today = date.today()
today_sub = '2022-04-08'

def fetchSession(url):
    session = HTMLSession()
    r = session.get(url)
    return r

def getTrades(r):
    table = r.html.find('table')[0]
    rows = table.find('tr')
    return rows[1:]

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


def scrapeAllTradesToday():
    r = fetchSession('https://sec.report/Senate-Stock-Disclosures')
    trades = getTrades(r)
    n = len(trades)
    all_trades = []
    l1_head = [
        'file date', 'trade', 'senator'
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
            for h,e in zip(l1_head, l1_elements):
                trade.append(h)
                trade.append(e.text)
            for h,e in zip(l2_head, l2_elements):
                trade.append(h)
                trade.append(e.text)
            trade[1] = trade[1][:10]
            # today_sub used #
            if str(today_sub) != trade[1]:
                current = False
                break
            trade[7] = trade[7].split('\n', 1)[0]
            trade[9] = value_to_ints(trade[9])
            trade = arr_to_dict(trade)
            all_trades.append(trade)
    return all_trades

def determineLargeTrades(all_trades):
    large_trades = []
    for t in all_trades:
        if t['value'][1] > 15001:
            large_trades.append(
                 {
                'trade' : t['trade'],
                'trade type' : t['trade type'],
                'value' : t['value'],
                'senator' :t['senator']
                }
            )
    return large_trades

def main():
    all_trades = scrapeAllTradesToday()
    large_trades = determineLargeTrades(all_trades)
    with open('daily_trades.txt', 'w') as f:
        for t in large_trades:
            for (key,item) in t.items():
                f.write(
                    '%s : %s\n' % (
                       key,item
                    )
                )
            f.write('\n')

if __name__ == "__main__":
    main()