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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from io import StringIO



def get_data():
    url = 'https://www.ebay.co.uk/sch/i.html?_dcat=22610&_fsrp=1&_from=R40&_nkw=jvc+projector&_sacat=0&LH_PrefLoc=2&LH_ItemCondition=3000&_udhi=200&_sop=15&rt=nc&LH_BIN=1'
    url_2 = 'https://www.ebay.co.uk/sch/i.html?_from=R40&_nkw=jvc%20projector&_sacat=0&LH_TitleDesc=0&_fsrp=1&LH_Auction=1&_dcat=22610&_sop=1&LH_PrefLoc=2&LH_ItemCondition=3000&rt=nc'
    r_2 = requests.get(url_2)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    soup_2 = BeautifulSoup(r_2.text, 'html.parser')
    return soup, soup_2

def parse(soup):
    productslist = []
    results = soup.find_all('div', {'class': 's-item__info clearfix'})
    for item in results:
        product = {
            'title': item.find('div', {'class': 's-item__title'}).text,
            'price': float((item.find('span', {'class': 's-item__price'}).text.replace(',', ''))[1:]),
            'type': item.find_all_next('div', {'class': 's-item__detail s-item__detail--primary'})[1].text
            # 'solddate': item.find('span', {'class': 's-item__title--tagblock__COMPLETED'}).find('span', {'class':'POSITIVE'}).text
        }
        productslist.append(product)
    return productslist

def output_1(productslist):
    productsdf =  pd.DataFrame(productslist[1:])
    productsdf.to_csv('./output_offer.csv', index=False)
    print('Saved to CSV')
    return

def output_2(productslist):
    productsdf =  pd.DataFrame(productslist[1:])
    productsdf.to_csv('./output_auction.csv', index=False)
    print('Saved to CSV')
    return


def df_combiner(product_list_offer, product_list_auction):
    # joining the offer and auction dfs
    offer_df = pd.DataFrame(product_list_offer[1:])
    auction_df = pd.DataFrame(product_list_auction[1:])
    auction_df['type'] = 'auction'
    joined = pd.concat([auction_df, offer_df])
    print(len(joined))
    # # adding ID column
    # joined = joined.reset_index()
    # joined['ID'] = joined.index + 1
    # joined = joined.drop('index', axis = 1)
    # # filtering the dataframe based on type
    joined = joined[~((joined['type'] == 'Buy it now') & (joined['price'] > 175))]
    joined = joined[~((joined['type'] == 'or Best Offer') & (joined['price'] > 200))]
    joined = joined[~((joined['type'] == 'auction') & (joined['price'] > 175))]
    print(len(joined))
    joined.to_csv('./new_df.csv', index=False)
    print('combiner run successfully')
    return



def final_df_creator(old, new):
    merged = old.merge(new, how='outer', indicator=True)
    unique_df2 = merged[merged['_merge'] == 'right_only'].drop(columns='_merge')
    # df_combined = pd.concat([df1, df2]).drop_duplicates(keep=False)
    return unique_df2



soup = get_data()[0]
productslist = parse(soup)
output_1(productslist)
soup_2 = get_data()[1]
productslist_2 = parse(soup_2)
output_2(productslist_2)

df_combiner(productslist, productslist_2)

# saving the original dataframe and the one to compare to

# old_df = pd.read_csv('old_df.csv')
# new_df = pd.read_csv('new_df.csv')





# PORT = 587
# EMAIL_SERVER = "smtp-mail.outlook.com"  # Adjust server address, if you are not using @outlook

# # # Load the environment variables
# # current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
# # envars = current_dir / ".env"
# # load_dotenv(envars)

# # Read environment variables
# sender_email = os.environ.get('USER_EMAIL')
# password_email = os.environ.get('USER_PASSWORD')

# print(sender_email, password_email)


# textStream = StringIO()
# # df.to_csv(textStream,index=False)


# #
# def send_email(old_df, new_df):
#     # Create the base text message.
#     msg = MIMEMultipart()
#     # msg.attach(MIMEApplication(textStream.getvalue(), Name=filename))
#     msg["Subject"] = "List of JVC's"
#     msg["From"] = sender_email
#     msg["To"] = sender_email
#     msg.attach(MIMEText("Here's the list of JVC's"))
#     # with open("new_df.csv", "rb") as f:
#     #     attached_file = MIMEApplication(f.read(), _subtype="csv")
#     #     attached_file.add_header(
#     #         "content-disposition",
#     #         "attachment",
#     #         filename="JVC_list.csv",
#     #     )
#     #     msg.attach(attached_file)
#     # # msg.set_content(
#     # #     f"""\
#     # #     Here's the latest JVC's.
#     # #     """
#     # # )
#     if len(old_df) == len(new_df):
#         old_df = old_df
#         new_df=new_df
#         with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
#             server.starttls()
#             server.login(sender_email, password_email)
#             server.sendmail(sender_email, sender_email, msg.as_string())


#     # setting conditions under which to send email
#     elif (len(old_df) != len(new_df)):
#         output_df = final_df_creator(old_df, new_df)
#         output_df.to_csv('./new_df.csv', index=False)
#         old_df = new_df
#         new_df = output_df
#         old_df.to_csv('./old_df.csv', index=False)
#         with open("new_df.csv", "rb") as f:
#             attached_file = MIMEApplication(f.read(), _subtype="csv")
#             attached_file.add_header(
#                 "content-disposition",
#                 "attachment",
#                 filename="JVC_list.csv",
#             )
#             msg.attach(attached_file)
#         # msg.set_content(
#         #     f"""\
#         #     Here's the latest JVC's.
#         #     """
#         # )
#         with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
#             server.starttls()
#             server.login(sender_email, password_email)
#             server.sendmail(sender_email, sender_email, msg.as_string())
#             server.sendmail(sender_email, sender_email, msg.as_string())

#     return



# send_email(old_df, new_df)

# # old_df = sender_email(old_df)
# # new_df = sender_email(new_df)


# # def send_emails():
# #     df = pd.read_csv('old_df.csv')
# #     df = df[df['best offer'] == 'or Best Offer']
# #     if len(df) > 1:
# #         send_email()
# #
# # send_emails()



# # @app.lib.cron()
# # def cron_job(event):
# #     df = load_df(URL)
# #     result = query_data_and_send_emails(df)
# #     return result
