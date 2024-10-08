import requests
from bs4 import BeautifulSoup
import concurrent.futures


def filter_terms(title_dictionary, terms):
    filtered_links = set()

    for key in title_dictionary:
        for title in title_dictionary[key]:
            for term in terms:
                if term in title:
                    filtered_links.add(title)


def filter_links(website_links, website_url):
    filtered_links = set()
    for link in website_links:
        for link in website_links[link]:
            if website_url in link:
                filtered_links.add(link)
    website_links = filtered_links
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
def build_link_dictionary(soup,website_URL):
    website_links = {}
    url_index = 0
    website_title = soup.find("title")
    try:
        website_links[website_title.string] = get_all_links(soup,website_URL)
     #   print(website_title.string)
      #  print(website_links[website_title.string])
    except AttributeError:
        pass
    url_index += 1
    return website_links

#breaks without internet connection, exception handling needed
def make_soup(url):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup
    except requests.exceptions.ConnectionError:
        print("Connection error occurred while trying to fetch the URL:", url)
        return None

def format_website(url):
    soup = make_soup(url)
    return soup


def get_titles_with_term(term, filtered_links):
    titles_with_term = []

    def process_link(link):
        try:
            formated_page = make_soup(link)
        except requests.exceptions.RequestException as e:
            print(f"Request error occurred while trying to fetch the URL {link}: {e}")
            return None

        if formated_page is not None:
            page_title = formated_page.find("title")
            if page_title and term in page_title.get_text():
                return (page_title.get_text(), link)
        return None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_link = {executor.submit(process_link, link): link for link in filtered_links}
        for future in concurrent.futures.as_completed(future_to_link):
            link = future_to_link[future]
            result = future.result()
            if result:
                titles_with_term.append(result)

    return titles_with_term




