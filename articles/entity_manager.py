from .scraper import format_website, build_link_dictionary, filter_links, get_titles_with_term,make_soup
import logging
from datetime import datetime
from .models import Article
import time
from .rss_scraper import gather_data, filter_data
from .config_handler import load_config, read_config_data


def update_database():
    websites, terms = load_config()
    website_names, url_dict, website_rss_list, rss_dict = read_config_data(websites)
    #with rss feed
    for website_name in website_names:
        if rss_dict.get(website_name) != "none":
            print(website_name)
            data_dictionary = gather_data(website_name, rss_dict.get(website_name))
            data_dictionary, term_dict = filter_data(website_name, data_dictionary, terms)
            #print(term_dict)
            for term in terms:
                for pair in term_dict[term]:
                    print(pair)
                    existing_article = Article.objects.filter(title=pair[0]).first()
                    if not existing_article:
                        logging.info("Új cím hozzáadása: " + pair[0] + " " + website_name + " " + str(datetime.now()))
                        article = Article(title=pair[0], term=term, website=website_name)
                        article.save()
                #print(pair)
        else:
            #magyar nemzet case ide
            print("website does not have rss feed")
            #without rss feed
            soup = make_soup(url_dict[website_name])
            logging.info("linkek gyűjtése" + str(datetime.now()))
            link_dict = build_link_dictionary(soup, url_dict[website_name])
            #print(website_links)
            filtered_links = filter_links(link_dict, url_dict[website_name])
            #print(filtered_links)
            for term in terms:
                titles_with_term = get_titles_with_term(term, filtered_links)
                for pair in titles_with_term:
                    existing_article = Article.objects.filter(title=pair[0]).first()
                    if not existing_article:
                        logging.info("Új cím hozzáadása: " + pair[0] + " " + website_name + " " + str(datetime.now()))

                        article = Article(title=pair[0], term=term, website=website_name)
                        article.save()
            logging.info("Adatbázis frissítve" + str(datetime.now()))

    def periodic_task():
        while True:
            update_database()  # Call your function
            time.sleep(900)  # Sleep for 5 minutes (300 seconds)

