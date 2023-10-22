from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render
from .forms import ExpressionForm
from .models import Article,Update  # Import your model for data storage
import requests
from bs4 import BeautifulSoup
import urllib.error
import threading
import time



def print_value(request):
    if request.method == 'POST':
        submitted_value = request.POST.get('expression', '')
        # You can print the value or perform any other action here
        print(submitted_value)
    return HttpResponse(submitted_value)


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


def format_html(link):
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
        index = format_html(indexpage)
        formatedIndices.append(index)
    return formatedIndices

def get_titles_with_term(term, website_links):
    links = {}
    for key in website_links:
        titles_with_term = []
        for link in website_links[key]:
            try:
                formated_page = format_html(link)
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

def update_database():
    terms = "Orbán", "Gyurcsány"
    website_list = ["https://www.origo.hu", "https://444.hu", "https://telex.hu", "https://magyarnemzet.hu/"]
    websites = format_websites(website_list)
    print("linkek gyűjtése")
    website_links = build_link_dictionary(websites, website_list)
    website_links = filter_links(website_links, website_list)
    for term in terms:
        titles_with_term = get_titles_with_term(term, website_links)
        for website, titles in titles_with_term.items():
            for title in titles:
                existing_article = Article.objects.filter(title=title).first()
                if not existing_article:
                    print("Új cím hozzáadása:",title,website)
                    article = Article(title=title, term=term, website=website)
                    article.save()
    print("Adatbázis frissítve")

def get_terms_on_sites(request):
    if request.method == 'GET':
        submitted_values = request.GET.getlist('expression')  # Get a list of submitted expressions


        articles = Article.objects.filter(term__in=submitted_values)  # Retrieve articles with terms in the submitted list

        return render(request, 'articles.html', {'articles': articles})

    return HttpResponse("Form submitted successfully")

def view_articles(request):
    if request.method == 'GET':
        submitted_value = request.GET.get('expression', '')
        articles = Article.objects.filter(term=submitted_value)  # Retrieve all articles from the database
        return render(request, 'articles.html', {'articles': articles})
    return HttpResponse("Form submitted successfully")

def periodic_task():
    while True:
        update_database()  # Call your function
        time.sleep(900)  # Sleep for 5 minutes (300 seconds)


def start_periodic_task(request):
    periodic_thread = threading.Thread(target=periodic_task)
    periodic_thread.daemon = True  # This ensures the thread terminates when the main program does
    periodic_thread.start()
    return HttpResponse("Adatbázis frissítése")

def list_updates(request):
    updates = Update.objects.all()
    return render(request, 'update_list.html', {'updates': updates})

def index(request):
    updates = Update.objects.all()
    return render(request, 'index.html',{'updates': updates})