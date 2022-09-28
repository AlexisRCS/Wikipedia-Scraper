import requests
from bs4 import BeautifulSoup
import re
import json


cache = {}
def hashable_cache(f):
    """
    the function hashable_cache is a decorator, it will speed up the browsing trough wikipedia 
    by using some session memory and previous results cache memory, it has 1 argument (f).

    argument :
        f = the browsing function to speed up, the function f has to be construct with 2 arguments (url,session)
    
    requirement :
         to work properly, the function hashable_cache require an external dict variable named cache --> cache = {...}
    """
    def inner(url,session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner


@hashable_cache
def get_first_paragraph(wikipedia_url,session) :
    """
    the function get_first_paragraph will extract the first paragraph from a wikipedia page 
    by analyzing htlm data, it has 2 arguments (wikipedia_url and session).

    argument :
        wikipedia_url = the url of the wikipedia page to scrape
        session = request.Session() an object that contain usefull data to improve browsing
    """
    wikipedia_content = session.get(wikipedia_url).text
    wikipedia_soup = BeautifulSoup(wikipedia_content, "html.parser")
    paragraphs = wikipedia_soup.find_all("p") 
    for paragraph in paragraphs :
        if paragraph.find("b") != None :
            first_paragraph = str(paragraph)
            first_paragraph =re.sub("<(?:\"[^\"]*\"['\"]*|'[^']*'['\"]*|[^'\">])+>","",first_paragraph)
            first_paragraph =re.sub("\[.+\]","",first_paragraph)
            first_paragraph =re.sub("\(.+\)","",first_paragraph)
            first_paragraph =re.sub("\{.+\}","",first_paragraph)
            return first_paragraph


def get_leaders() :
    """
    the function get_leaders will extract data from the site : https://country-leaders.herokuapp.com, navigate inside these data 
    in order to find the leaders wikipedia urls (extract the first paragraph trough the get_first_paragraph function) 
    and compile all the data inside a dictionary as an output (return).
    """
    cookies_url = "https://country-leaders.herokuapp.com/cookie"
    countries_url = "https://country-leaders.herokuapp.com/countries"
    leaders_url = "https://country-leaders.herokuapp.com/leaders"
    session = requests.Session()
    cookies = session.get(cookies_url).cookies
    countries_list = session.get(countries_url, cookies = cookies).json()
    leaders_per_country = {}
    for country in countries_list :
        if  session.get(leaders_url,cookies = cookies, params = {"country" : country}).status_code == 403 :
            cookies = session.get(cookies_url).cookies
        leaders = session.get(leaders_url,cookies = cookies, params = {"country" : country}).json()
        leaders_per_country[country] = []
        for leader in leaders :
            wikipedia_url = leader["wikipedia_url"]
            leader["first_paragraph"] = get_first_paragraph(wikipedia_url,session)
            leaders_per_country[country].append(leader)
    return leaders_per_country


def save() :
    """
    the function save() will save the output of the get_leaders function in leaders.json file and also save the cache in cache.json file 
    """
    with open("leaders.json", "w") as my_file:
        json.dump(get_leaders(),my_file)
    with open("cache.json", "w") as my_file:
        json.dump(cache,my_file)


if __name__ == '__main__' :
    save()