import json
from bs4 import BeautifulSoup
import requests
from .scraper import load_config

#url = requests.get('https://telex.hu/rss')

def gather_titles():
    print("gathering")
    config = load_config()
    websites = config.get("websites", [])
    terms = config.get("terms", [])
    rss_list = []
    titles = []
    links = []
    for website_info in websites:
        website_rss = website_info.get("website_rss")
        rss_list.append(website_rss)

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