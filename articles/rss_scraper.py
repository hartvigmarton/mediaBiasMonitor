import json
from bs4 import BeautifulSoup
import requests
from .config_handler import load_config


def gather_data(website_name,rss):
    data = {}
    data_list = []
    try:
        url = requests.get(rss)
    except requests.exceptions.ConnectionError:
        print("Connection refused by", website_name)

    soup = BeautifulSoup(url.content,'xml')
    entries = soup.find_all('item')
    for entry in entries:
        article_data = []
        title = entry.title.text
        article_data.append(title)
        link = entry.link.text
        article_data.append(link)
        pub_date = entry.pubDate.text
        article_data.append(pub_date)

        data_list.append(article_data) #make it list with title,link,date
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
                data_list.append(pair)
                articles_with_term.append(pair)
        term_dict[term] = articles_with_term
    filtered_data[website_name] = data_list
    return filtered_data, term_dict

