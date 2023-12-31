import json
from bs4 import BeautifulSoup
import requests
from .config_handler import load_config

#url = requests.get('https://telex.hu/rss')

def gather_data(website_name,rss):
    data = {}
    print("gathering data")
    data_list = []
    url = requests.get(rss)
    soup = BeautifulSoup(url.content,'xml')
    entries = soup.find_all('item')
    for entry in entries:
        title = entry.title.text
        link = entry.link.text
        pair = (title,link)
        data_list.append(pair)
     #   print(f"Title :{title}\n\nLink: {link}\n\n")
    data[website_name] = data_list
    return data

def filter_data(website_name,data_dictionary,terms):
    filtered_data = {}

    data_list = []
    term_dict = {}
    for term in terms:
        articles_with_term = []
        for pair in data_dictionary.get(website_name):
            if term in pair[0]:
               # print(pair[0])
                #articles_with_term.append(pair)
                data_list.append(pair)
                articles_with_term.append(pair)
        term_dict[term] = articles_with_term
    filtered_data[website_name] = data_list
    return filtered_data, term_dict

