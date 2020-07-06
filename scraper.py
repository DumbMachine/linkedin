import os
import json
import pickle
import selenium

from tqdm import tqdm
from person import ProfileScraper
from bs4 import BeautifulSoup as soup

driver = selenium.webdriver.Firefox(
    executable_path="/home/weakstation/work/geckodriver")
cookies = pickle.load(
    open("/home/weakstation/work/linkedin/cookies.pkl", "rb"))

driver.get("https://www.linkedin.com")

for cookie in cookies:
    driver.add_cookie(cookie)

usernames = [i.split("/")[2] for i in json.load(
    open("/home/weakstation/work/linkedin/raw/facebook.list.json", "r"))]

for username in tqdm(usernames, total=len(usernames)):
    filename = f"/home/weakstation/work/linkedin/data/{username}"
    if not os.path.isfile(filename):
        scraper = ProfileScraper(driver)
        profile = scraper.scrape(user=username)

        with open(filename, "w") as file:
            json.dump(profile.to_dict(), file)
