import json


def load_config():
    try:
        with open('articles/config/config.json', 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            websites = config.get("websites", [])  # ez és a következő sor mehetnek a load_configba
            terms = config.get("terms", [])
        return websites,terms
    except FileNotFoundError:
        raise Exception("Config file not found")


def read_config_data(websites):
    website_names = []
    url_dict = {}
    website_rss_list = []
    rss_dict = {}
    for website_info in websites:
        website_url = website_info.get("website_url")
        website_rss = website_info.get("website_rss")
        website_rss_list.append(website_rss)
        website_name = website_info.get("website_name")
        website_names.append(website_name)
        rss_dict[website_name] = website_rss
        url_dict[website_name] = website_url
    return website_names, url_dict, website_rss_list, rss_dict
