from scraper import format_website, build_link_dictionary, filter_links, get_titles_with_term,make_soup
import logging
from datetime import datetime
from models import Article
import time
from rss_scraper import gather_data, filter_data
from config_handler import load_config, read_config_data
from datetime import date,datetime
import os
# Make sure Django environment is set up
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()
today = date.today()

logfile_name = "log/" + str(today) + ".log"
logging.basicConfig(filename=logfile_name, encoding='utf-8', level=logging.INFO)


def update_database():
    websites, terms = load_config()
    website_names, url_dict, website_rss_list, rss_dict = read_config_data(websites)

    for website_name in website_names:
        # with rss feed
        if rss_dict.get(website_name) != "none":
            print(website_name)
            data_dictionary = gather_data(website_name, rss_dict.get(website_name))
            data_dictionary, term_dict = filter_data(website_name, data_dictionary, terms)
            for term in terms:
                for data in term_dict[term]:
                    print(data)
                    existing_article = Article.objects.filter(title=data[0], term=term).first()
                    if not existing_article:
                        logging.info("Új cím hozzáadása: " + data[0] + " " + website_name + " " + str(datetime.now()))
                        article = Article(title=data[0], term=term, website=website_name, link=data[1],pub_date=data[2])
                        article.save()
        else:
            #magyar nemzet,ripost case ide
            print(website_name,"website does not have rss feed")
            #without rss feed
            try:
                soup = make_soup(url_dict[website_name])
            except UnboundLocalError:
                print("Nincs kapcsolat a weboldallal")
                break
            logging.info("linkek gyűjtése" + str(datetime.now()))
            link_dict = build_link_dictionary(soup, url_dict[website_name])
            filtered_links = filter_links(link_dict, url_dict[website_name])
            for term in terms:
                titles_with_term = get_titles_with_term(term, filtered_links)
                for data in titles_with_term:
                    existing_article = Article.objects.filter(title=data[0]).first()
                    if not existing_article:
                        logging.info("Új cím hozzáadása: " + data[0] + " " + website_name + " " + str(datetime.now()))

                        article = Article(title=data[0], term=term, website=website_name, link=data[1])
                        article.save()
            logging.info("Adatbázis frissítve" + str(datetime.now()))
    print("Művelet befejezve", str(datetime.now()))

if __name__=="__main__":
    update_database()