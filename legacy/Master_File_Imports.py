from emailFunc import *
from getTradesFunc import *
from screenerFunc import *

def main():
    # for testing use 
    justToday = False

    if justToday:
        today = datetime.today()
        trades = scrapeAllTradesToday(today)
    else:
        trades = scrapeAllTrades()

    # get both large equity purchases and any small cap equity purchases
    large_purchases = getLargeEquity(trades)
    print('large purchases fetched.')
    small_caps = getSmallCaps(trades)
    print('small caps fetched.')
    print(large_purchases)
    print(small_caps)

    trades = large_purchases.extend(small_caps)

    with open('data/daily_trades.txt', 'w') as f:
        for t in trades:
            for (key,item) in t.items():
                f.write(
                    '%s : %s\n' % (
                       key,item
                    )
                )
            f.write('\n')
    print('trade scrape complete.')
    # sendEmail()

if __name__ == "__main__":
    main()