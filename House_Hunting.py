# To get the information we need, import the following:
import requests
from bs4 import BeautifulSoup
# To be able to email the information, import these:
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
# Other useful imports:
import re
import pandas


## Getting the webpage and its source from Rightmove.

def get_source(url):
    page = requests.get(url)
    source_text = page.text.encode('utf8')
    soup = BeautifulSoup(source_text, 'html.parser')
    return soup

def get_property_page(prop):
    url = "http://www.rightmove.co.uk"+prop
    page = requests.get(url)
    source_text = page.text.encode('utf8')
    soup = BeautifulSoup(source_text, 'html.parser')
    return soup

## Get URLs for homes near all underground stations.

tube_map = get_source("http://www.rightmove.co.uk/tube-map.html")

tube_codes = []

for link in tube_map.find_all('a'):
    a = link.get('href')
    if "?locationIdentifier=STATION" in a:
        tube_codes.append(str(a.split("=")[2]))


## Rightmove doesn't always filter for Cash-buyers
## even when you tell it to.
## Nor does it have the option to filter for Help to Buy.

def get_description(soup):
    text = []
    for i in soup.find_all('div', {'class':"sect"}):
        text.append(str(i).upper())
    return text

def cash_buyer(description):
    cash = []
    for i in description:
        if "CASH BUYER ONLY" in i or "CASH BUYERS ONLY" in i or "CASH ONLY" in i:
            cash.append(i)
    if len(cash) > 0:
        return "yes"
    else:
        return "no"

def help_to_buy(description):
    help_ = []
    for i in description:
        if "HELP TO BUY" in i or "HELPTOBUY" in i:
            help_.append(i)
    if len(help_) > 0:
        return "yes"
    else:
        return "no"

## Rightmove only ever shows the top 42 pages. (On my laptop at least)
## This means that it will show the top 42 x 25 = 1050 properties.

## Before going through each page separately, we will need to know how many pages there are for each search.

## To get the total number of properties found based on your criteria:

def total_pages_found(Station,Min_Bed,Max_Price,Min_Price):
    url = "http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier="+Station+"&minBedrooms="+Min_Bed+"&maxPrice="+Max_Price+"&minPrice="+Min_Price+"&sortType=2&index=0&includeSSTC=false&viewType=LIST&dontShow=sharedOwnership%2Cretirement&areaSizeUnit=sqft&currencyCode=GBP"
    soup = get_source(url)
    #Get the total properties for the given criteria. This can be used to decide how many properties you want to look at.
    totals = []
    for i in soup.find_all(id = 'searchHeader'):
        totals.append(str(i.find('span')))
    regex = r"(\d+)"
    total = []
    for i in totals:
        for t in re.findall(regex, i):
            total.append(t)

    total_properties = int( ''.join(total) )

    if total_properties > 1025:
        return 42
    else:
        return total_properties / 25



## Get a list of the URLs all the properties in your criteria:

def search_results(Min_Bed,Max_Price,Min_Price,Station,Cash,Help):
    #Must put quotation marks around variables.
    good_properties = []
    total_pages = total_pages_found(Station,Min_Bed,Max_Price,Min_Price)


    pages = []
    for i in range(0,total_pages + 1):
        pages.append(i*24)

    #Get Property urls
    for n in pages:
        url = "http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier="+Station+"&minBedrooms="+Min_Bed+"&maxPrice="+Max_Price+"&minPrice="+Min_Price+"&sortType=2&index="+str(n)+"&includeSSTC=false&viewType=LIST&dontShow=sharedOwnership%2Cretirement&areaSizeUnit=sqft&currencyCode=GBP"

        soup = get_source(url)

        urls = []
        for link in soup.find_all('a'):
            urls.append(link.get('href'))
        properties = []
        for i in urls:
            if "property-for-sale/property" in str(i):
                properties.append(i)
        refined_prop = set(properties)
        property_urls = []
        for i in refined_prop:
            if "property-0.html" not in i:
                property_urls.append(str(i))
    #Search Proprties
        for i in property_urls:

            prop_descriptions = get_description(get_property_page(i))

            if cash_buyer(prop_descriptions) == Cash and help_to_buy(prop_descriptions) == Help:
                good_properties.append("http://www.rightmove.co.uk"+i)


    return good_properties



df1 = pandas.DataFrame(search_results('0','320000','160000',i,"no","yes") for i in tube_codes)
df2 = pandas.DataFrame(search_results('0','220000','160000',i,"no","no") for i in tube_codes)



## Save properties to csv

df1.to_csv("Properties_H2B.csv")
df2.to_csv("Properties_Non-H2B.csv")

## Email properties to whomever

fromaddr = "arianna.salili@gmail.com"
toaddr = "arianna_salili@hotmail.com"

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Help-To-Buy Properties"


body = "Attached is a list of properties in London with Help-to-Buy."

msg.attach(MIMEText(body, 'plain'))

filename = "Properties_H2B.csv"
attachment = open("C:/Users/arian/Documents/Programming/Python/House-Hunting/Properties_H2B.csv", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

filename = "Properties_Non-H2B.csv"
attachment = open("C:/Users/arian/Documents/Programming/Python/House-Hunting/Properties_Non-H2B.csv", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "Bertrand.Postulate2")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
