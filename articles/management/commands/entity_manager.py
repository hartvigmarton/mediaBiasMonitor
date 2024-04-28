import logging
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.db import connection  # Import Django's database connection
from ...scraper import format_website, build_link_dictionary, filter_links, get_titles_with_term, make_soup
from ...models import Article
from ...rss_scraper import gather_data, filter_data
from ...config_handler import load_config, read_config_data

today = date.today()
logfile_name = "log/" + str(today) + ".log"
logging.basicConfig(filename=logfile_name, encoding='utf-8', level=logging.INFO)


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            websites, terms = load_config()
            website_names, url_dict, website_rss_list, rss_dict = read_config_data(websites)

            for website_name in website_names:
                try:
                    logging.info("címek gyűjtése a következő oldalról: " + website_name + " " + str(datetime.now()))
                    if rss_dict.get(website_name) != "none":
                        data_dictionary = gather_data(website_name, rss_dict.get(website_name))
                        data_dictionary, term_dict = filter_data(website_name, data_dictionary, terms)
                        for term in terms:
                            for data in term_dict[term]:
                                existing_article = Article.objects.filter(title=data[0], term=term).first()
                                if not existing_article:
                                    logging.info("Új cím hozzáadása: " + data[0] + " " + website_name + " " + str(datetime.now()))
                                    article = Article(title=data[0], term=term, website=website_name, link=data[1], pub_date=data[2])
                                    article.save()
                    else:
                        print(website_name, "website does not have rss feed")
                        try:
                            logging.info(" soup = make_soup(url_dict[website_name]) started on " + website_name + " " +
                                         str(datetime.now()))
                            soup = make_soup(url_dict[website_name])
                            logging.info(" soup = make_soup(url_dict[website_name]) finished on " + website_name + " " +
                                         str(datetime.now()))

                        except Exception as soup_error:
                            logging.error(f"Error occurred while making soup for {website_name}: {soup_error}")
                            continue

                        logging.info("linkek gyűjtése" + str(datetime.now()))
                        logging.info(" link_dict = build_link_dictionary(soup, url_dict[website_name]) started on " + website_name + " " + str(
                            datetime.now()))

                        link_dict = build_link_dictionary(soup, url_dict[website_name])
                        logging.info(
                            " link_dict = build_link_dictionary(soup, url_dict[website_name]) ended on " + website_name + " " + str(
                                datetime.now()))
                        logging.info(
                            "  filtered_links = filter_links(link_dict, url_dict[website_name]) started on " + website_name + " " + str(
                                datetime.now()))
                        filtered_links = filter_links(link_dict, url_dict[website_name])
                        logging.info(
                            "  filtered_links = filter_links(link_dict, url_dict[website_name]) ended on " + website_name + " " + str(
                                datetime.now()))
                        for term in terms:
                            logging.info(
                                "  titles_with_term = get_titles_with_term(term, filtered_links) started on " + website_name + " " + str(
                                    datetime.now()))
                            titles_with_term = get_titles_with_term(term, filtered_links)
                            logging.info(
                                "  titles_with_term = get_titles_with_term(term, filtered_links) ended on " + website_name + " " + str(
                                    datetime.now()))
                            for data in titles_with_term:
                                existing_article = Article.objects.filter(title=data[0]).first()
                                if not existing_article:
                                    logging.info("Új cím hozzáadása: " + data[0] + " " + website_name + " " + str(datetime.now()))
                                    article = Article(title=data[0], term=term, website=website_name, link=data[1])
                                    article.save()
                except Exception as inner_error:
                    logging.error(f"Error occurred while processing {website_name}: {inner_error}")
                    continue

                logging.info("gyűjtés befejezve a következő oldalon: " + website_name + " " + str(datetime.now()))

        except Exception as outer_error:
            logging.error(f"Unexpected error occurred: {outer_error}")

        finally:
            # Close database connection
            connection.close()
            logging.info("Database connection closed")

            # Log completion
            logging.info("Adatbázis frissítve" + str(datetime.now()))
            print("Művelet befejezve", str(datetime.now()))
