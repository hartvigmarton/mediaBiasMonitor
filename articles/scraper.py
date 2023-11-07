from .models import Article,Blog_Post  # Import your model for data storage
import requests
from bs4 import BeautifulSoup
import urllib.error
import json
import os
import logging
from datetime import date,datetime

today = date.today()
logfile_name = "log/" + str(today) + ".log"
logging.basicConfig(filename=logfile_name, encoding='utf-8', level=logging.DEBUG)


def filter_links(website_links, website_list):
    website_index = 0
    for key in website_links:
        filtered_links = set()
        for link in website_links[key]:
            if website_list[website_index] in link:
                filtered_links.add(link)
        website_index += 1
        website_links[key] = filtered_links
    return website_links


#get all the subdomains of a website
def get_all_links(main_site, website_URL):
    links = []

    for link in main_site.find_all('a'):
        if str(link.get('href')).startswith("/"):
            title = main_site.find("title")
            links.append(website_URL + link.get('href'))
        elif link.get('href') is not None:
            links.append(link.get('href'))
    return links

#builds a dictionary with the name of the website as key and a list of links to the subdomains as value
def build_link_dictionary(formated_websites,website_URLs):
    website_links = {}
    url_index = 0
    for website in formated_websites:
        website_title = website.find("title")
        try:
            website_links[website_title.string] = get_all_links(website,website_URLs[url_index])
        except AttributeError:
            pass
        url_index += 1
    return website_links

#breaks without internet connection, exception handling needed
def make_soup(link):
    try:
        r = requests.get(link)
    except requests.exceptions.ConnectionError:
        print("connection error")
        pass
    soup = BeautifulSoup(r.text, 'lxml')
    return soup

def format_websites(indexpages):
    formatedIndices = []
    for indexpage in indexpages:
        soup = make_soup(indexpage)
        formatedIndices.append(soup)
    return formatedIndices

def get_titles_with_term(term, website_links):
    links = {}
    for key in website_links:
        titles_with_term = []
        for link in website_links[key]:
            try:
                formated_page = make_soup(link)
            except urllib.error.HTTPError:
                pass
            page_title = formated_page.find("title")
            try:
                if term in page_title.string:
                    titles_with_term.append(page_title.string)
            except (AttributeError,TypeError):
                pass
        links[key] = titles_with_term
    return links




