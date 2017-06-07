#Home Criteria:

Min_Bed = "1"
Min_Price = "150000"
Max_Price = "350000"
Cash = "no" #put yes if you want cash-only homes
lower_price = "210000" #This is the lower maximum for non Help to Buy homes.

#Email details:

fromaddr = "from@email.com"
toaddr = "to@email.com"
password = ""



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
  
        
station_codes_names = []
for link in tube_map.find_all('a'):

    a = link.get('href')
    b = link.get('title')
    if "STATION^" in str(a) and "Property for sale near" in str(b):
        u = str(a).split("=")[2]
        
        station_codes_names.append([u,str(b).replace('Property for sale near ','')])


## Rightmove doesn't always filter for Cash-buyers
## even when you tell it to.
## Nor does it have the option to filter for Help to Buy.

def get_description(soup):
    text = []
    for i in soup.find_all('div', {'class':"sect"}):
        text.append(str(i).upper())
    return text

def cash_buyer(description):
    if re.search(r"cash(?i)", str(description)):
        return "yes"
    else:
        return "no"

def help_to_buy(description):
    if re.search(r"help(| )to(| )buy(?i)",str(description)):
        return "yes"
    else:
        return "no"

def get_price(soup):
    for i in soup.find_all('div', {'class': 'row one-col property-header'}):
        price = str(i.find('strong'))
        if "POA" not in str(price):
            u = re.findall(r"\d+",price)
            return int( ''.join(u) )
        else:
            return 0


## Rightmove only ever shows the top 42 pages. (On my laptop at least)
## This means that it will only show the top 42 x 25 = 1050 properties.

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
        return int(total_properties / 25)



## Get a list of the URLs all the properties in your criteria:


good_properties =[]

property_urls = []

print "Getting urls of properties near stations\n"


for code in station_codes_names:
    Station = code[0]
    total_pages = total_pages_found(Station,Min_Bed,Max_Price,Min_Price)
    if total_pages > 0:
        pages = []
        for i in range(0,total_pages + 1):
            pages.append(i*24)
        #t = 0
        for n in pages:
            url = "http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier="+Station+"&minBedrooms="+Min_Bed+"&maxPrice="+Max_Price+"&minPrice="+Min_Price+"&sortType=2&index="+str(n)+"&includeSSTC=false&viewType=LIST&dontShow=sharedOwnership%2Cretirement&areaSizeUnit=sqft&currencyCode=GBP"
            #t+=1

            soup = get_source(url)
            #print t
            urls = []
            for link in soup.find_all('a'):
                urls.append(link.get('href'))
            properties = []
            for i in urls:
                if "property-for-sale/property" in str(i):
                    properties.append(i)
            refined_prop = set(properties)

            for i in refined_prop:
                if "property-0.html" not in i and i not in zip(*property_urls)[0]: #Need to edit this to make it more efficient.
                    property_urls.append([str(i),code[1]])

print "Searching each property that matches criteria.\n"

H2B = []
NH2B = []

for x in property_urls:
    i = x[0]
    prop_descriptions = get_description(get_property_page(i))

    if help_to_buy(prop_descriptions) == "yes":
        H2B.append(["http://www.rightmove.co.uk"+i,x[1]])

    else:
        price = get_price(get_property_page(i))
        if cash_buyer(prop_descriptions) == Cash and  0 < price < int(lower_price) :
            NH2B.append(["http://www.rightmove.co.uk"+i,x[1]])

## Save properties to csv

print "Saving properties to CSV\n"



df1 = pandas.DataFrame(H2B)
df2 = pandas.DataFrame(NH2B)



df1.to_csv("Properties_H2B.csv")
df2.to_csv("Properties_Non-H2B.csv")

## Email properties to whomever

print "Sending email\n"

fromaddr = "arianna.salili@gmail.com"
toaddr = "arianna_salili@hotmail.com"

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Help-To-Buy Properties"


body = "Attached is a list of properties in London with Help-to-Buy."

msg.attach(MIMEText(body, 'plain'))

filename = "Properties_H2B.csv"
# Add path of file

attachment = open("C:/Users/arian/Documents/Programming/Python/House-Hunting/Properties_H2B.csv", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

filename = "Properties_Non-H2B.csv"
# Add path of file
attachment = open("C:/Users/arian/Documents/Programming/Python/House-Hunting/Properties_Non-H2B.csv", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, password)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()

print "Done!"
