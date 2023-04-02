import requests
from bs4 import BeautifulSoup
import pandas as pd

import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from dotenv import load_dotenv  # pip install python-dotenv

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText



def get_data():
    url = 'https://www.ebay.co.uk/sch/i.html?_dcat=22610&_fsrp=1&_from=R40&_nkw=jvc+projector&_sacat=0&LH_PrefLoc=2&LH_ItemCondition=3000&_udhi=200&_sop=15&rt=nc&LH_BIN=1'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def parse(soup):
    productslist = []
    results = soup.find_all('div', {'class': 's-item__info clearfix'})
    for item in results:
        product = {
            'title': item.find('div', {'class': 's-item__title'}).text,
            'price': float((item.find('span', {'class': 's-item__price'}).text)[1:]),
            'best offer': item.find_all_next('div', {'class': 's-item__detail s-item__detail--primary'})[1].text
            # 'solddate': item.find('span', {'class': 's-item__title--tagblock__COMPLETED'}).find('span', {'class':'POSITIVE'}).text
        }
        productslist.append(product)
    return productslist

def output(productslist):
    productsdf =  pd.DataFrame(productslist)
    productsdf.to_csv('C:/Users/liamc/Coding Projects/Ebay JVC/output.csv.gzip', compression='gzip', index=False)
    productsdf.to_csv('C:/Users/liamc/Coding Projects/Ebay JVC/output.csv', index=False)
    print('Saved to CSV')
    return

soup = get_data()
productslist = parse(soup)
output(productslist)



PORT = 587
EMAIL_SERVER = "smtp-mail.outlook.com"  # Adjust server address, if you are not using @outlook

# Load the environment variables
current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = current_dir / ".env"
load_dotenv(envars)

# Read environment variables
sender_email = os.getenv("EMAIL")
password_email = os.getenv("PASSWORD")


def send_email():
    # Create the base text message.
    msg = EmailMessage()
    msg["Subject"] = "List of JVC's"
    msg["From"] = sender_email
    msg["To"] = sender_email
    with open('output.csv.gzip', 'rb') as file:
        # Attach the file with filename to the email
        msg.attach(MIMEApplication(file.read(), Name='output.csv.gzip'))

    msg.set_content(
        f"""\
        Here's the latest JVC's.
        """
    )

    with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
        server.starttls()
        server.login(sender_email, password_email)
        server.sendmail(sender_email, sender_email, msg.as_string())




def send_emails():
    df = pd.read_csv('output.csv')
    df =df[df['best offer'] == 'or Best Offer']
    if len(df) > 1:
        send_email()

send_emails()



# @app.lib.cron()
# def cron_job(event):
#     df = load_df(URL)
#     result = query_data_and_send_emails(df)
#     return result