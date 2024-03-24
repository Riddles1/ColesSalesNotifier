import requests
from bs4 import BeautifulSoup
import time
from email.message import EmailMessage
import ssl
import smtplib
from datetime import datetime
from dotenv import dotenv_values
import pandas as pd

CSV_FILE_PATH = r".config/Items.csv"
DOTENV_FILE_PATH = r".config\email_credentials.env"
SLEEP_TIME = 60*60*6

#This program is designed to run constantly (in my case, on a Raspberry Pi)
#Note, this program relies heavily on the format of the Coles website and that Coles continues to sell the products in the ITEMS list

#This pulls in my email credentials into a dict from my .env file 
CONFIG = dotenv_values(DOTENV_FILE_PATH)
#This loads in the Items csv as a dataframe
df = pd.read_csv(CSV_FILE_PATH)

#function that's purpose is to send me an email with a subject and a body if called
def email(subject, body):
    email_sender = CONFIG['email_sender']
    email_password = CONFIG['email_password']
    email_receiver = CONFIG['email_receiver']

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    
def fetch_page(item_position):
    max_retries = 5  # Maximum number of retries
    retries = 0
    
    while retries < max_retries:
        try:
            page = requests.get(df['URL'][item_position]) 
        except Exception as e:
            print(f"Failed to request the page for '{df['Item Full Name'][item_position]}'")
            time.sleep(120) #wait 2mins before trying again
            continue    
        soup = BeautifulSoup(page.content, 'html.parser')
        #find the location in the html that contains the price
        price_html = soup.find("span", class_="price__value")
        #extract the price value out of that information
        #the below few lines are a complicated way of making sure that the price_value is correct for any number of digits in the price value
        first_index = str(price_html).find('$') + 1
        second_index = (str(price_html)[first_index:]).find('"') + first_index
        #Check if the page has actually returned correctly
        if str(price_html)[first_index: second_index] == "Non":
            retries += 1
            continue
        price_value = float(str(price_html)[first_index: second_index])
        break
    return price_value

PREVIOUS_EMAILS_TIMESTAMPS = []

#main loop
while True:
    items_on_sale = []
    #iterate through the items i'm interested in and request their page on Coles' website
    for item_position in range(len(df['URL'])):
        #fetch the page and return the price value
        price_value = fetch_page(item_position)
        #check if the price is in the target range
        if price_value <= df['Target Price'][item_position]:
            #if so, add the item to a list along with it's current price so I can be emailed about it
            items_on_sale.append([item_position, price_value])
            print(f"The current price of {df['Item Nickname'][item_position]} is ${'{:,.2f}'.format(price_value)} | (below the target value of ${'{:,.2f}'.format(df['Target Price'][item_position])})")
        else:
            print(f"The current price of {df['Item Nickname'][item_position]} is ${'{:,.2f}'.format(price_value)}") 
    #check if I have already been emailed today
    if PREVIOUS_EMAILS_TIMESTAMPS == [] or PREVIOUS_EMAILS_TIMESTAMPS[-1] != datetime.now().strftime("%d/%m/%Y"):
        #if not, check whether there are any items on sale and if so, send me an email with the items that are on sale
        if items_on_sale != []:
            subject = "Items on Sale!"
            body = ""
            #include every item in the email, each on a separate line
            for item in items_on_sale:
                body += f"{df['Item Full Name'][item[0]]} is now ${'{:,.2f}'.format(item[1])}\n"
            email(subject, body)
            print('\n--- email has been sent ---')
            #add the timestamp that email was sent to a list to look at later to make sure I'm not emailed more than once a day
            PREVIOUS_EMAILS_TIMESTAMPS.append(datetime.now().strftime("%d/%m/%Y"))
    #wait 3 hours before checking prices again
    print()
    time.sleep(SLEEP_TIME)