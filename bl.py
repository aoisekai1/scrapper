from array import array
from ast import Param, keyword
from email import header
from fileinput import filename
from multiprocessing.dummy import Array
from operator import le
from wsgiref import headers
from bs4 import BeautifulSoup
import requests
import sys
import os
import json
import time
import random
from datetime import datetime
import csv

def url_modfy():
    data = []
    with open('data.json') as item:
        data = json.load(item)
        
    return data

def res_html(URL_KEYWORD, USER_AGENT, URL_PAGINATION=""):
    url = "https://www.bukalapak.com/products?search%5Bkeywords%5D="+URL_KEYWORD

    if URL_PAGINATION != "":
        url = URL_PAGINATION

    headers = {
        "User-Agent": USER_AGENT #"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }

    req = requests.get(url, headers=headers)
    sop = BeautifulSoup(req.content, 'html.parser')
    if req.status_code != 200:
        print('Ops sorry something error, Please check again later ')
        return False
    
    return sop

def setting_url(URL_JSON):
    with open('data.json','w') as f:
        json.dump(URL_JSON, f)

def check_pagination(URL_KEYWORD, USER_AGENT):
    print('Please wait...')
    sop = res_html(URL_KEYWORD, USER_AGENT)
    pagination = sop.find('ul', class_="bl-pagination__list")
    if pagination == None:
        return False
    else:
        os.system('clear')
        return True

def menu():
    USER_AGENT = ""
    URL_KEYWORD = input("Enter Keyword: ")
    PAGE_NUM_FROM = input("Enter Page Number From: ")
    PAGE_NUM_TO = input("Enter Page Number To: ")

    if not os.path.exists('user_agent.json'):
        USER_AGENT = input("Enter User Agent: ") #"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        json_user_agent = {
            "user_agent": USER_AGENT 
        }

        with open('user_agent.json', 'w') as f:
            json.dump(json_user_agent, f)
    else:
        try:
            data = json.load(open('user_agent.json', encoding='utf-8'))
            USER_AGENT = data['user_agent']
        except ValueError:
            print("User agent not found, Please remove file user_agent.json and try again")
            return False

    if URL_KEYWORD == "" or USER_AGENT == "":
        print("Keyword / User agent not found")
        return False

    return {"URL_KEYWORD": URL_KEYWORD, "USER_AGENT":USER_AGENT, 'PAGE_NUM_FROM': PAGE_NUM_FROM, 'PAGE_NUM_TO': PAGE_NUM_TO}

def progress(i, total):
    persen = (i*100/total)
    sys.stdout.write('\r')
    sys.stdout.write("[%-1s] (%s/%s)" % ('#'*int(persen), i, total))
    sys.stdout.flush()
    time.sleep(0.25)

def scrapper_bl():
    key = menu()

    url_config = []
    data_products = []
    # keyword = key['URL_KEYWORD'].upper()
    tot = 0
    is_pagination = check_pagination(key['URL_KEYWORD'], key["USER_AGENT"])
   
    if is_pagination and key["PAGE_NUM_FROM"] != "" and key["PAGE_NUM_TO"] != "":
        print("Started scrapping web ...")
    
        i = int(key['PAGE_NUM_FROM'])
        while i <= int(key['PAGE_NUM_TO']):
            data_url = {
                "link": 'https://www.bukalapak.com/products?page='+str(i)+'&search%5Bkeywords%5D='+key['URL_KEYWORD']
            }
            url_config.append(data_url)
            i+=1

        setting_url(url_config)
        list_url = url_modfy()
       
        # data_products.append("\n ============================================== \n")
        # data_products.append("\n Product "+keyword.strip()+" BukaLapak\n")
        # data_products.append("\n ============================================== \n")

        count_p = 0
        num =int(key['PAGE_NUM_FROM'])
        
        for item in list_url:
            sop = res_html(key['URL_KEYWORD'], key["USER_AGENT"], item["link"])
            # keyword = sop.find('h1', class_="bl-text--subheading-3").text
            products = sop.find_all('div', class_='bl-product-card')
            tot += len(products)
            # data_products.append("\n PRODUK HALAMAN KE-"+str(num)+"\n")
            for product in products:
                count_p += 1
                progress(count_p, tot)
                title_product = product.find('div', class_="bl-product-card__description-name").text
                price_product = product.find('p', class_="bl-text--subheading-20").text
                link_product = product.find('div', class_="bl-product-card__description-name").p.a['href']
                card_p = product.find('div', class_="bl-product-card__description-rating-and-sold")
                rate_product = card_p.find('div', class_="bl-product-card__description-rating")
                if rate_product != None:
                    rate_product = str(rate_product.text.strip())
                else:
                    rate_product = "0"

                sell_product = card_p.select('p')

                if len(sell_product) != 0 and len(sell_product) == 2:
                    sell_product = str(sell_product[1].text.strip())
                else:
                    sell_product = "0"

                tag_product = product.find('div', class_="bl-product-card__description-store")
                location_product = tag_product.find('span', class_="bl-product-card__location").text
                store_product = tag_product.find('span', class_="bl-product-card__store").text

                # product_temp = str(count_p)+'. '+title_product.strip()+" | "+str(price_product.strip())+" | "+sell_product+" | "+rate_product
                list_product = []
                list_product.append(str(count_p))
                list_product.append(title_product.strip())
                list_product.append(str(price_product.strip()))
                list_product.append(sell_product)
                list_product.append(rate_product)
                list_product.append(store_product)
                list_product.append(location_product)
                list_product.append(link_product)

                data_products.append(list_product)
            
            num+=1
                
    else:
        print("Started scrapping web ...")
    

    # print(data_products)
    if len(data_products) > 0:
        # group_data_products = "\n".join(data_products)
        header = [
            'No','Poroduct Name', 'Price','Selling',
            'Rate','Store','Location', 'Link'
        ]
        date = datetime.date(datetime.now())
        x = random.randint(0, 100)

        if not os.path.exists(key['URL_KEYWORD']):
            os.makedirs(key['URL_KEYWORD'])
        
        filename = key['URL_KEYWORD']+'/'+"product_"+key['URL_KEYWORD']+"_"+str(date)+str(x)+".csv"
        with open(filename, 'w',  encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)

            # write multiple rows
            writer.writerows(data_products)
    else:
        print('\nPlease try again\n')
    
    print('\n')
    print('=========================================== \n')
    print('Keyword: '+key["URL_KEYWORD"].upper()+'\n')
    print('Total data: '+str(len(data_products))+'\n')
    print('Scrapping web finished \n')
    print('=========================================== \n')
    
    confirm = input('Scrapping again (Y/N): ')
    if confirm.upper() == "Y":
        os.system("clear")
        os.system("python bl.py")

scrapper_bl()
