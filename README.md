# Senate Trading Tracker

<p>The goal of this program is to find small, under the radar companies whose equity has recently been disclosed as being purchased by US senators.</p>

[This python file](/main/ScrapeTradesToday.py) tracks market trading activity of US senators, and discerns which of these trades are of most interest. The script scrapes the [SEC EDGAR Insider Trading Disclosures List](https://sec.report/Senate-Stock-Disclosures) and searches for trades which have been filed on the current day. The script then determines if the traded asset was purchased, and if the asset was an equity. If so, the equity market cap and trade size are measured to classify the trade as important, in which case an alert is sent via email. All equity purchases of over $100,000, regardless of market cap, are important. Trades of medium cap firms (market cap between $2B and $10B) which value of at least $50,000 are important, and all small cap equities traded are important. This logic stems from the idea that a senator trading a very small bank, manufacturer, or other firm is significantly more interesting than trading a larger firm - think Google or Goldman Sachs. The [information for each trade](/res/daily_trades.json) is saved to a ```.json``` file, the content of which is formatted using ```html``` and sent as an email. The information included in each trade alert is:

- Ticker traded
- Date traded
- Date filed
- Senator
- Equity description
- Trade value
- Market cap

In addition, I also feed the equity information to [Google News](https://news.google.com/topstories?hl=en-US&gl=US&ceid=US:en), retrieve the top 3 most recent/relevant articles, and send those to the user under the main content. The ticker in the body header also contains a link to the equity's [Yahoo Finance](https://finance.yahoo.com/) description page. Here's an example of an alert email:

![](/res/repo_pics/sample_alert.JPG)

<i>Note that there are actually not 38 days between the trade and file date. This is calcuated as the difference between the run date and trade date. Since this screen grab was from testing, this counter is wrong as it assumes the current date and filing date are the same.</i>

The program is run via a [batch file](/tools/run_trades.bat) two times on a daily basis, on market close and market open, to keep me updated on any potential trades that may be worth researching more. I made this as a side project while studying at Lehigh University, and I hope you find it interesting!

<b> If you are interested in being added to the email list, or have any other questions, please email:
ders.mailbot@gmail.com</b>