import requests
from bs4 import BeautifulSoup
import time
from email.message import EmailMessage
import ssl
import smtplib
from datetime import datetime

#This program is designed to run constantly on a Raspberry Pi
#Note, this program relies heavily on the format of 

ITEMS = {"https://www.coles.com.au/product/rana-four-cheese-ravioli-325g-3091159": ["Rana Four Cheese Ravioli", "Rana", 6.00],
         "https://www.coles.com.au/product/sirena-lemon-and-pepper-tuna-95g-9658379": ["Sirena Lemon & Pepper Tuna", "Sirena", 2.00],
         "https://www.coles.com.au/product/mccain-frozen-cheese-and-bacon-pizza-slices-6-pack-600g-8544829": ["McCain Frozen Cheese & Bacon Pizza Slices 6 pack", "Pizza Slices", 5.00],
         "https://www.coles.com.au/product/lynx-aerosol-black-antiperspirant-165ml-3722420": ["Lynx Aerosol Black Antiperspirant", "Lynx Black Deoderant", 5.00],
         "https://www.coles.com.au/product/lynx-men-body-wash-black-400ml-2225249": ["Lynx Men Body Wash Black", "Lynx Black Body Wash", 4.00],
         "https://www.coles.com.au/product/palmolive-naturals-body-wash-pomegranate-mango-1l-8180212": ["Palmolive Naturals Body Wash Pomegranate Mango", "Palmolive Body Wash", 6.00],
         "https://www.coles.com.au/product/john-west-tempters-tuna-chunks-in-springwater-95g-7532777": ["John West Tempters Tuna Chunks in Springwater", "John West Tuna", 1.50],
         "https://www.coles.com.au/product/sunrice-jasmine-rice-cup-2-pack-250g-8478509": ["Sunrice Jasmine Rice Cup 2 pack", "Rice Cups", 2.00],
         "https://www.coles.com.au/product/nivea-black-and-white-clear-invisible-aerosol-antiperspirant-deodorant-250ml-1996403": ["Nivea Black & White Clear Invisible Aerosol Antiperspirant Deodorant", "Am's Nivea Deo", 5]
         }
PREVIOUS_EMAILS_TIMESTAMPS = []

#function that's purpose is to send me an email with a subject and a body if called
def email(subject, body):
    email_sender = 'pyemail123@gmail.com'
    email_password = 'emailpassword123'
    email_receiver = 'emailreceiver123@gmail.com'

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


#main loop
while True:
    items_on_sale = []
    #iterate through the items i'm interested in and request their page on Coles' website
    for item_url in ITEMS:
        try:
            page = requests.get(item_url) 
        except:
            print("there was an exception here")
            time.sleep(60) #wait 60 seconds before trying again
            continue
        #parse that request into BeautifulSoup so that it's html can be analysed
        soup = BeautifulSoup(page.content, 'html.parser')
        #find the location in the html that contains the price
        price_html = soup.find("span", class_="price__value")
        #extract the price value out of that information
        #the below few lines are a complicated way of making sure that the price_value is correct for any number of digits in the price value
        first_index = str(price_html).find('$') + 1
        second_index = (str(price_html)[first_index:]).find('"') + first_index
        price_value = float(str(price_html)[first_index: second_index])
        print(f"The current price of {ITEMS[item_url][1]} is ${price_value}") 
        #check if the price is in the target range
        if price_value <= ITEMS[item_url][2]:
            #if so, add the item to a list along with it's current price so I can be emailed about it
            items_on_sale.append([item_url, price_value])
    #check if I have already been emailed today
    if PREVIOUS_EMAILS_TIMESTAMPS == [] or PREVIOUS_EMAILS_TIMESTAMPS[-1] != datetime.now().strftime("%d/%m/%Y"):
        #if not, check whether there are any items on sale and if so, send me an email with the items that are on sale
        if items_on_sale != []:
            subject = "Items on Sale!"
            body = ""
            #include every item in the email, each on a separate line
            for item in items_on_sale:
                body += f"{ITEMS[item[0]][0]} is now ${item[1]}\n"
            email(subject, body)
            #add the timestamp that email was sent to a list to look at later to make sure I'm not emailed more than once a day
            PREVIOUS_EMAILS_TIMESTAMPS.append(datetime.now().strftime("%d/%m/%Y"))
    #wait 3 hours before checking prices again
    print()
    time.sleep(10800)