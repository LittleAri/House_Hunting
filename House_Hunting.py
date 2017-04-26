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

## To only get homes near the underground/overgound/DLR:
## (Can't rely on the rail in London)

def get_stations(soup):
    stations = []
    for i in soup.find_all('div', { 'class' : 'clearfix nearest-stations'}):
        stations.append(str(i))
    return stations


def good_transport(stations):
    trains = []
    for i in stations:
        if "light" in i or "london-overground" in i or "london-underground" in i:
            trains.append(i)
    if len(trains) > 0:
        return "yes"
    else:
        return "no"

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

## To get the total number of properties found based on your criteria:

def total_properties_found(Min_Bed,Max_Price,Min_Price,Radius):
    url = "http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&minBedrooms="+Min_Bed+"&maxPrice="+Max_Price+"&minPrice="+Min_Price+"&numberOfPropertiesPerPage=24&radius="+Radius+"&sortType=2&index=0&includeSSTC=false&viewType=LIST&dontShow=sharedOwnership%2Cretirement&areaSizeUnit=sqft&currencyCode=GBP"
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
    return str(total_properties)

## Get a list of the URLs all the properties in your criteria:

def search_results(Min_Bed,Max_Price,Min_Price,Props_Per_Page,Radius,Cash,Help,Tran):
    #Must put quotation marks around variables.
    #Only radius options are [0.0,0.25,0.5,1.0,3.0,5.0,10.0,15.0,20.0,30.0,40.0]
    url = "http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&minBedrooms="+Min_Bed+"&maxPrice="+Max_Price+"&minPrice="+Min_Price+"&numberOfPropertiesPerPage="+Props_Per_Page+"&radius="+Radius+"&sortType=2&index=0&includeSSTC=false&viewType=LIST&dontShow=sharedOwnership%2Cretirement&areaSizeUnit=sqft&currencyCode=GBP"
    soup = get_source(url)
    #Get Property urls
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
    good_properties = []
    for i in property_urls:
        nearby_stations = get_stations(get_property_page(i))
        prop_descriptions = get_description(get_property_page(i))

        if cash_buyer(prop_descriptions) == Cash and help_to_buy(prop_descriptions) == Help and good_transport(nearby_stations) == Tran:
            good_properties.append("http://www.rightmove.co.uk"+i)
    print "Total Properties Found:"
    print len(good_properties)
    print "\nProperties in descending price order:\n"

    return good_properties

total = total_properties_found("0","320000","160000","3.0")


df1 = pandas.DataFrame(search_results('0','320000','160000',total,'3.0',"no","yes","no"))
df2 = pandas.DataFrame(search_results('0','220000','160000',total,'3.0',"no","no","yes"))

## Save properties to csv

df1.to_csv("Properties_H2B.csv")
df2.to_csv("Properties_Non-H2B.csv")

## Email properties to whomever

fromaddr = "from address"
toaddr = "to address"

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Help-To-Buy Properties"


body = "Attached is a list of properties in London with Help-to-Buy."

msg.attach(MIMEText(body, 'plain'))

filename = "Properties_H2B.csv"
attachment = open("C:/Users/arian/Downloads/Properties_H2B.csv", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

filename = "Properties_Non-H2B.csv"
attachment = open("C:/Users/arian/Downloads/Properties_Non-H2B.csv", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "password")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
