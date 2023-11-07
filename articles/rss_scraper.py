import json
from bs4 import BeautifulSoup
import requests
from .entity_manager import load_config

#url = requests.get('https://telex.hu/rss')

def gather_titles():
    print("gathering")
    config = load_config()
    website_data = config.get("websites", [])
    terms = config.get("terms", [])
    rss_list = []
    titles = []
    links = []
    website_names = []

    for website_info in website_data:
        website_rss = website_info.get("website_rss")
        rss_list.append(website_rss)
        website_name = website_info.get("website_name")
        website_names.append(website_name)


    for rss in rss_list:
        if rss != "none":
            url = requests.get(rss)
            soup = BeautifulSoup(url.content,'xml')
            print(soup.title.text)
            entries = soup.find_all('item')


        for entry in entries:
            title = entry.title.text
            link = entry.link.text
            titles.append(title)
            print(f"Title :{title}\n\nLink: {link}\n\n")
    return titles