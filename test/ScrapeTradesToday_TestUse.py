# use for backtesting changes 

from requests_html import HTMLSession
from datetime import datetime,timedelta
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import re 
from bs4 import BeautifulSoup
import nums_from_string

def fetchSession(url):
    session = HTMLSession()
    r = session.get(url)
    return r

def getTrades(r):
    table = r.html.find('table')[0]
    rows = table.find('tr')
    return rows[1:]

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

def getHTML(url):
    r = fetchSession(url)
    h = r.text
    doc = BeautifulSoup(h, 'html.parser')
    return doc

def getTicker(trade_):
    try:
        return re.findall('\[(.*?)\]', trade_)[0]
    except IndexError:
        return ''

def getFirstRowEntry(ticker):
    url = 'https://finance.yahoo.com/quote/{}/'.format(ticker)
    soup = getHTML(url)
    quote_summary = soup.find(id='quote-summary')
    if quote_summary is None:
        return ''
    tables = quote_summary.find_all('table')
    if len(tables) == 0:
        return ''
    # right side table
    mc_table = tables[1]
    # get all rows
    mc_rows = mc_table.find_all('td')
    # entire row 
    mc_string = str(mc_rows[1])
    return mc_string

def isStock(row_one):
    flag = 'data-test="(.*)-value'
    seach = re.search(
        flag, row_one
    )
    if seach is None:
        return -1
    marker = seach.group(1)
    if marker == 'MARKET_CAP':
        return 1
    elif marker == 'NET_ASSETS':
        return 0
    # N/A
    else:
        return -1

def parseToMillions(value_string):
    unit = value_string[-1:]
    number = nums_from_string.get_nums(value_string)[0]
    #keep in units of millions
    if unit == 'B':
        number = number * 1000
    elif unit == 'T':
        number = number * 1000000
    return number

def getNAVCAP(row_one):
    value = re.search('>(.*)<', row_one).group(1)
    if value == 'N/A':
        return -1
    return round(parseToMillions(value),2)

def cleanNewsURLQuery(trade):
    return (
        'https://news.google.com/search?q={}&hl=en-US&gl=US&ceid=US%3Aen'.format(
            trade.replace(' ', '%20').replace(',', '').replace('[','%5B').replace(']','%5D')
            )
        )

def getArticleTextFromUrl(url):
    soup = getHTML(url)
    articles = soup.find_all('article')
    return str(articles)

def findNOccurrence(str, sub, n):
    val = -1
    for i in range(0,n):
        val = str.find(sub, val + 1)
    return val

def getNewsUrlsTitles(full_article_string):
    list_of_urls_titles = []
    list_of_articles = full_article_string.split('</article>')
    i = 0
    for a in list_of_articles[:-1]:
        if i > 2:
            break
        start_ind = findNOccurrence(
            a, 'href', 2
        )
        slice = a[start_ind:]
        url = slice[slice.find('articles'):slice.find('">')]
        title = slice[slice.find('>'):slice.find('<')][1:]
        list_of_urls_titles.append(
            {
                'title':title,
                'url':'news.google.com/{}'.format(url)
            }
        )
        i += 1
    return list_of_urls_titles

def writeTradeToFile(trade, path):
    with open(path, 'w') as f:
        for (key,item) in trade.items():
            if key == 'Yahoo!':
                f.write(
                    '%s\n' % (
                    item
                    )
                )
            else:
                f.write(
                    '%s : %s\n' % (
                    key,item
                    )
                )
        f.write('\n')

def writeToFile(trades, path):
    with open(path, 'w') as f:
        for t in trades:
            for (key,item) in t.items():
                if key == 'Yahoo!':
                    f.write(
                        '%s\n' % (
                        item
                        )
                    )
                else:
                    f.write(
                        '%s : %s\n' % (
                        key,item
                        )
                    )
            f.write('\n')

def getHTMLNews(t):
    return open('res/html/format.html').read().format(
                quote_link = t['Yahoo!'],
                ticker = getTicker(t['Equity']),
                trade_date = t['Trade Date'],
                file_date = t['File Date'],
                senator = t['Senator'],
                trade = t['Equity'],
                value = t['Trade Value'],
                mkt_cap = t['Market Cap'],
                news_url1 = t['URL1'],
                news_title1 = t['Title 1'],
                news_url2 = t['URL2'],
                news_title2 = t['Title 2'],
                news_url3 = t['URL3'],
                news_title3 = t['Title 3']
            )

def getHTMLNoNews(t):
    return open('res/html/format_no_news.html').read().format(
                quote_link = t['Yahoo!'],
                ticker = getTicker(t['Equity']),
                trade_date = t['Trade Date'],
                file_date = t['File Date'],
                senator = t['Senator'],
                trade = t['Equity'],
                value = t['Trade Value'],
                mkt_cap = t['Market Cap']
            )

def scrapeImportantTrades(today=datetime.today().date(), onlyToday=False, backtest=False, backtestDate='2022-04-01'):
    r = fetchSession('https://sec.report/Senate-Stock-Disclosures')
    # if website is down
    try:
        trades = getTrades(r)
    except IndexError:
        print('website may be down. quitting.')
        sys.exit(1)

    n = len(trades)
    all_trades = []
    dt_backtest = datetime.strptime(backtestDate, '%Y-%m-%d').date()

    for i in range(0,n,2):
        imp_trade = False
        l1_elements = trades[i].find('td')
        l2_elements = trades[i+1].find('td')[:-1]

        # make sure trade happened today before doing anything 
        file_date, trade_date = l1_elements[0].text.split('\n')
        if file_date != str(today) and onlyToday:
            break

        if backtest:
            file_dt = datetime.strptime(file_date, '%Y-%m-%d').date()
            days = file_dt - dt_backtest
            if days < timedelta(days=0):
                break

        # ensure trade is a purchase, otherwise contniue to next trade
        trade_type = l2_elements[0].text.split('\n', 1)[0]
        if trade_type != 'Purchase':
            continue

        trade = l1_elements[1].text
        senator = l1_elements[2].text
        senator = senator.split(' [')[0]
        value = value_to_ints(l2_elements[1].text)
        
        ticker = getTicker(trade)
        # move on if ticker is invalid
        if ticker == '':
            continue

        row_one = getFirstRowEntry(ticker)
        mkt_cap = getNAVCAP(row_one)
        small_mktCap = mkt_cap < 2000 and mkt_cap > 0
        medium_mktCap = mkt_cap >= 2000 and mkt_cap <= 10000
        large_mktCap = mkt_cap > 10000
        # any small caps, medium purchase medium caps, large purchase large cap
        if isStock(row_one) and small_mktCap:
            imp_trade = True
            cap_string = 'small'
        elif isStock(row_one) and medium_mktCap and value[0] >= 50000:
            imp_trade = True
            cap_string = 'medium'
        elif isStock(row_one) and large_mktCap and value[0] >= 100000:
            imp_trade = True
            cap_string = 'large'

        if imp_trade:
            url = 'https://finance.yahoo.com/quote/{}/'.format(ticker)
            trade_dict = {
                'trade date' : trade_date,
                'file date' : file_date,
                'senator' : senator,
                'trade' : trade,
                'trade type' : trade_type,
                'value' : value,
                'mkt cap' : cap_string,
                'yahoo finance' : url,
            }
            all_trades.append(trade_dict)
    return all_trades

def formatForEmail(trades_list):
    trades_for_txt = []
    for t in trades_list:
        trade_date = str(t['trade date']) + ' (' + str((
                datetime.today().date() - datetime.strptime(
                    t['trade date'], '%Y-%m-%d'
                ).date()
            )).split(',')[0] + ' ago)'

        value_string = '$' + (
            "{:,}".format(t['value'][0])
        ) + ' to $' + (
            "{:,}".format(t['value'][1])
        )

        if t['mkt cap'] == 'small':
            mkt_cap_string = 'Small Cap (Under $2B)'
        elif t['mkt cap'] == 'medium':
            mkt_cap_string = 'Medium Cap ($2B to $10B)'
        else:
            mkt_cap_string = 'Large Cap (Over $10B)'

        list_of_titles_urls = getNewsUrlsTitles(
            getArticleTextFromUrl(
                cleanNewsURLQuery(
                    t['trade']
                )
            )
        )

        if len(list_of_titles_urls) > 1:
            trades_for_txt.append(
                {
                    'Trade Date' : trade_date,
                    'File Date' : t['file date'],
                    'Senator' : t['senator'],
                    'Equity' : t['trade'],
                    'Trade Value' : value_string,
                    'Market Cap' : mkt_cap_string,
                    'Yahoo!' : t['yahoo finance'],
                    'Title 1' : list_of_titles_urls[0]['title'], 
                    'Title 2' : list_of_titles_urls[1]['title'],  
                    'Title 3' : list_of_titles_urls[2]['title'], 
                    'URL1' : list_of_titles_urls[0]['url'],
                    'URL2' : list_of_titles_urls[1]['url'],
                    'URL3' : list_of_titles_urls[2]['url']
                }
            )
        else:
            trades_for_txt.append(
                {
                    'Trade Date' : trade_date,
                    'File Date' : t['file date'],
                    'Senator' : t['senator'],
                    'Equity' : t['trade'],
                    'Trade Value' : value_string,
                    'Market Cap' : mkt_cap_string,
                    'Yahoo!' : t['yahoo finance']
                }
            )

    return trades_for_txt

def sendEmails(trades, toList = False):
    port = 465

    # login info
    with open('res/account_info.txt', 'r') as f:
        lines = f.readlines()
        send_email = lines[0]
        password = lines[1]

    # get list of emails from text file in data folder 
    recipients = []
    if toList:
        with open('res/mailing_list.txt','r') as f:
            lines = f.readlines()
        for l in lines:
            recipients.append(l.strip())
    else:
        recipients = [send_email]

    writeToFile(trades,'res/daily_trades.txt')

    for t in trades:
        writeTradeToFile(t, 'res/trade_for_html.txt')
        with open('res/trade_for_html.txt','r') as f:
            data = f.read()
        # if the length of the string from the file is not 0, then there was a 
        # (major) trade executed today
        if len(data) != 0:
            message = MIMEMultipart('alternative')
            message['Subject'] = 'Trade Alert'
            message['From'] = send_email
            message['To'] = ', '.join(recipients) # change post testing
            message['Bcc'] = ''

            body = MIMEText(data, 'plain')
            if len(t) == 13:
                html_string = getHTMLNews(t)
            # no news bullets 
            else:
                html_string = getHTMLNoNews(t)

            formatting = MIMEText(html_string, 'html')

            message.attach(body)
            message.attach(formatting)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
                server.login(send_email, password)
                server.sendmail(
                    send_email, recipients, message.as_string()
                )

def main():

    onlyToday = False
    backtest = True
    toList = False
    backtestDate = '2022-04-05'

    trades = scrapeImportantTrades(onlyToday=onlyToday, backtest=backtest, backtestDate=backtestDate)
    trades_for_mail = formatForEmail(trades)
    sendEmails(trades=trades_for_mail, toList=toList)

if __name__ == '__main__':
    main()