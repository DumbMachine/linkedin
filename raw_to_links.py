import os
import json
import pickle
from selenium import webdriver

from tqdm import tqdm
from bs4 import BeautifulSoup as soup

companies = ["facebook", "google", "twitter", "youtube", "instagram"]

stpage = 0
edpage = 40

company = "facebook"
startpage = "https://www.linkedin.com/search/results/people/?keywords={company}&origin=SWITCH_SEARCH_VERTICAL&page={page}"

driver = webdriver.Firefox(
    executable_path="/home/weakstation/work/geckodriver")
cookies = pickle.load(
    open("/home/weakstation/work/linkedin/cookies.pkl", "rb"))

driver.get("https://www.linkedin.com")
for cookie in cookies:
    driver.add_cookie(cookie)

with tqdm(total=(edpage-stpage)) as progress:
    for page in range(stpage, edpage):
        # getting the html page source
        driver.get(startpage.format(page=page, company=company))
        html = soup(driver.page_source, 'lxml')
        links = []
        links = [i['href'] for i in html.find_all('a')
                 if i.has_attr('href') and "/in/" in i['href']]

        if os.path.isfile(f"/home/weakstation/work/linkedin/raw/{company}.list.json"):
            alllinks = json.load(
                open(f"/home/weakstation/work/linkedin/raw/{company}.list.json", "r"))
            links += alllinks

        json.dump(list(set(links)), open(
            f"/home/weakstation/work/linkedin/raw/{company}.list.json", "w"))

        progress.update(1)
        progress.set_description(startpage.format(page=page, company=company))
