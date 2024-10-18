from bs4 import BeautifulSoup
import requests
import json

def readFile(city, xIdx, yIdx):
    details = []
    with open('%s-%d-%d.json' % (city, xIdx, yIdx)) as f:
        businesses = json.load(f)
        for business in businesses:
            business_details = {}
            business_details['business_name'] = business['details']['name']
            if 'website' in business['details']:
                business_details['website']= business['details']['website']
            else:
                business_details['website']= ''
            if 'formatted_phone_number' not in business['details']: #business is probably not real
                business_details['phone_number'] = 'invalid'
            else:
                business_details['phone_number']= business['details']['formatted_phone_number']
            business_details['address']=business['details']['formatted_address']
            business_details['rating']=business['rating']
            if('website' in business['details']):
                website_deets = scrapeInfo(business['details']['website'])
                if('booking_link' in website_deets):
                    business_details['booking_link'] = website_deets['booking_link']
            details.append(business_details)
    return details;
            


def scrapeInfo(url):
    deets = {}
    try:
        html_doc = requests.get(url)
        soup = BeautifulSoup(html_doc.text, 'html.parser')
        #check if we should be scraping the canonical url
        if(soup.find('link', rel='canonical')):
            canonical = soup.find('link', rel='canonical').get('href')
            if (url !=  canonical) :
                return scrapeInfo(canonical)
                                
        #iterate over each link and see if any of them are interesting
        for link in soup.find_all('a'):
            if('BOOK' in link.text.upper()):
                deets['booking_link'] = link.get('href')
        if 'booking_link' not in deets:
            webpage_text = soup.get_text().upper()
            if('BOOK' in webpage_text):
                if soup.find('div', class_='CareCruModal'):
                    deets['booking_link'] = 'https://www.carecru.com/'
    except:
        deets['booking_link'] = "invalid - was %s" % url
    return deets;  

def write_csv_headers(file):
    file.write("business_name, website, booking_link, phone_number, address, rating, reviews\n")

def write_csv_line(file, business_details):
    for detail in business_details:
        if('booking_link' in detail):
            booking_link = detail['booking_link']
        else:
            booking_link = ''
        file.write("%s, %s, %s, %s, %s, %s\n"
                % (detail['business_name'], 
                    detail['website'],  
                    booking_link, 
                    detail['phone_number'], 
                    detail['address'], 
                    detail['rating']));


def formatInfo(city):
    file = open("%s-businesses.csv" % city, 'w')
    write_csv_headers(file);
    for x in range(0, 1):
        for y in range(0, 1):
            business_details = readFile(city, x,y);
            write_csv_line(file, business_details);
    file.close();