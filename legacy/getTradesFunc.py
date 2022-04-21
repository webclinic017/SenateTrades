# add functions which get trade listings 
from requests_html import HTMLSession
import sys

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

def scrapeAllTrades():
    r = fetchSession('https://sec.report/Senate-Stock-Disclosures')
    trades = getTrades(r)
    n = len(trades)
    all_trades = []
    l1_head = [
        'trade date', 'file date', 'trade', 'senator'
    ]
    l2_head = [
        'trade type', 'value'
    ]
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
        trade[9] = trade[9].split('\n', 1)[0]
        trade[11] = value_to_ints(trade[11])
        trade = arr_to_dict(trade)
        all_trades.append(trade)
    return all_trades

def scrapeAllTradesToday(date_dt):
    r = fetchSession('https://sec.report/Senate-Stock-Disclosures')
    # if website is down
    try:
        trades = getTrades(r)
    except IndexError:
        print('website may be down. quitting.')
        sys.exit(1)

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
            # today_sub used #
            if str(date_dt) != trade[3]:
                current = False
                break
            trade[9] = trade[9].split('\n', 1)[0]
            trade[11] = value_to_ints(trade[11])
            trade = arr_to_dict(trade)
            all_trades.append(trade)
    return all_trades