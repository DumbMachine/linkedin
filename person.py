import time
import json

from scrape_linkedin.utils import AnyEC
from scrape_linkedin.Profile import Profile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class ProfileScraper:
    """
    Scraper for Personal LinkedIn Profiles. See inherited Scraper class for
    details about the constructor.
    """
    MAIN_SELECTOR = '.core-rail'
    ERROR_SELECTOR = '.profile-unavailable'

    def __init__(self, driver):
        self.timeout = 10
        self.driver = driver
        self.scroll_pause = 0.1
        self.scroll_increment = 300

    def scrape_by_email(self, email):
        self.load_profile_page(
            'https://www.linkedin.com/sales/gmail/profile/proxy/{}'.format(email))
        return self.get_profile()

    def scrape(self, url='', user=None):
        self.load_profile_page(url, user)
        return self.get_profile()

    def load_profile_page(self, url='', user=None):
        """Load profile page and all async content
        Params:
            - url {str}: url of the profile to be loaded
        Raises:
            ValueError: If link doesn't match a typical profile url
        """
        if user:
            url = 'http://www.linkedin.com/in/' + user
        if 'com/in/' not in url and 'sales/gmail/profile/proxy/' not in url:
            raise ValueError(
                "Url must look like... .com/in/NAME or... '.com/sales/gmail/profile/proxy/EMAIL")
        self.driver.get(url)
        # Wait for page to load dynamically via javascript
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.MAIN_SELECTOR)),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.ERROR_SELECTOR))
            ))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load profile.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the time out parameter in the Scraper
                   constructor
                3. Invalid e-mail address (or user does not allow e-mail scrapes) on scrape_by_email call
                """)

        # Check if we got the 'profile unavailable' page
        try:
            self.driver.find_element_by_css_selector(self.MAIN_SELECTOR)
        except:
            raise ValueError(
                'Profile Unavailable: Profile link does not match any current Linkedin Profiles')
        # Scroll to the bottom of the page incrementally to load any lazy-loaded content
        self.scroll_to_bottom()

    def get_profile(self):
        try:
            profile = self.driver.find_element_by_css_selector(
                self.MAIN_SELECTOR).get_attribute("outerHTML")
        except:
            raise Exception(
                "Could not find profile wrapper html. This sometimes happens for exceptionally long profiles.  Try decreasing scroll-increment.")
        contact_info = self.get_contact_info()
        return Profile(profile + contact_info)

    def get_contact_info(self):
        try:
            # Scroll to top to put clickable button in view
            self.driver.execute_script("window.scrollTo(0, 0);")
            button = self.driver.find_element_by_css_selector(
                'a[data-control-name="contact_see_more"]')
            button.click()
            contact_info = self.wait_for_el('.pv-contact-info')
            return contact_info.get_attribute('outerHTML')
        except Exception as e:
            print(e)
            return ""

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page
        Params:
            - scroll_pause_time {float}: time to wait (s) between page scroll increments
            - scroll_increment {int}: increment size of page scrolls (pixels)
        """
        expandable_button_selectors = [
            'button[aria-expanded="false"].pv-skills-section__additional-skills',
            'button[aria-expanded="false"].pv-profile-section__see-more-inline',
            'button[aria-expanded="false"].pv-top-card-section__summary-toggle-button',
            'button[data-control-name="contact_see_more"]'
        ]

        current_height = 0
        while True:
            for name in expandable_button_selectors:
                try:
                    self.driver.find_element_by_css_selector(name).click()
                except:
                    pass

            # Use JQuery to click on invisible expandable 'see more...' elements
            self.driver.execute_script(
                'document.querySelectorAll(".lt-line-clamp__ellipsis:not(.lt-line-clamp__ellipsis--dummy) .lt-line-clamp__more").forEach(el => el.click())')

            # Scroll down to bottom
            new_height = self.driver.execute_script(
                "return Math.min({}, document.body.scrollHeight)".format(current_height + self.scroll_increment))
            if (new_height == current_height):
                break
            self.driver.execute_script(
                "window.scrollTo(0, Math.min({}, document.body.scrollHeight));".format(new_height))
            current_height = new_height
            # Wait to load page
            time.sleep(self.scroll_pause)

    def wait(self, condition):
        return WebDriverWait(self.driver, self.timeout).until(condition)

    def wait_for_el(self, selector):
        return self.wait(EC.presence_of_element_located((
            By.CSS_SELECTOR, selector
        )))
