import pandas as pd 
from requests_html import HTMLSession
from lxml import html 
from datetime import date,datetime

today_sub = '2022-04-08'
today_sub_dt = datetime.strptime(
    today_sub, '%Y-%m-%d'
).date()

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


def scrapeAllTradesToday(date_datetime):
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
            if str(date_datetime) != trade[3]:
                current = False
                break
            trade[9] = trade[9].split('\n', 1)[0]
            trade[11] = value_to_ints(trade[11])
            trade = arr_to_dict(trade)
            all_trades.append(trade)
    return all_trades

def determineLargeTrades(all_trades, date_datetime):
    large_trades = []
    for t in all_trades:
        if t['value'][1] > 50001:
            # clean up data for presenation
            trade_date = str(t['trade date']) + ' (' + str((
                date_datetime - datetime.strptime(
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
                'Trade' : t['trade'],
                'Trade Type' : t['trade type'],
                'Value' : value_string,
                'Trade Date' : trade_date,
                'Senator' : t['senator']
                }
            )
    return large_trades

def main():
    # fix dates
    all_trades = scrapeAllTradesToday(today_sub_dt)
    large_trades = determineLargeTrades(all_trades, today_sub_dt)
    with open('data/daily_trades.txt', 'w') as f:
        for t in large_trades:
            for (key,item) in t.items():
                f.write(
                    '%s : %s\n' % (
                       key,item
                    )
                )
            f.write('\n')
    print('trade scrape complete.')

if __name__ == "__main__":
    main()