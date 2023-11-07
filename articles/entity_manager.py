from .scraper import format_websites,build_link_dictionary,filter_links,get_titles_with_term
import logging
import json
from datetime import date,datetime
from .models import Article
import time
import threading

def load_config():
    try:
        with open('articles/config/config.json', 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        raise Exception("Config file not found")


def update_database():
    config = load_config()
    websites = config.get("websites", [])
    terms = config.get("terms", [])
    website_list = []

    for website_info in websites:
        website_url = website_info.get("website_url")
        website_list.append(website_url)
    websites = format_websites(website_list)
    logging.info("linkek gyűjtése" + str(datetime.now()))
    website_links = build_link_dictionary(websites, website_list)
    website_links = filter_links(website_links, website_list)
    for term in terms:
        titles_with_term = get_titles_with_term(term, website_links)
        for website, titles in titles_with_term.items():
            for title in titles:
                existing_article = Article.objects.filter(title=title).first()
                if not existing_article:
                    logging.info("Új cím hozzáadása: " + title + " " + website + " " + str(datetime.now()))

                    article = Article(title=title, term=term, website=website)
                    article.save()
    logging.info("Adatbázis frissítve" + str(datetime.now()))

    def periodic_task():
        while True:
            update_database()  # Call your function
            time.sleep(900)  # Sleep for 5 minutes (300 seconds)

