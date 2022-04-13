import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def main():
    port = 465
    send_email = 'ders.mailbot@gmail.com'
    #receive_email = 'andersseline15@gmail.com'
    password = 'Mailbot15'

    with open('data/daily_trades.txt', 'r') as f:
        data = f.read()

    # if the length of the string from the file is not 0, then there was a 
    # major trade executed today
    if len(data) != 0:
        print('major trade found.')
        message = MIMEMultipart('alternative')
        message['Subject'] = 'Trade Alert'
        message['From'] = 'SenateStockWatch'
        message['To'] = send_email # change post testing
        message['Bcc'] = '' # for other recipients
        body = MIMEText(data, 'plain')
        message.attach(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
            server.login(send_email, password)
            server.sendmail(
                send_email, send_email, message.as_string()
            )
    else:
        print('no major trades.')

if __name__ == "__main__":
    main()