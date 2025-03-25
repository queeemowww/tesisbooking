from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import asyncio
import time


class Arrival():
    def __init__(self, delay = None):
        self.delay = delay
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(self.chrome_options)

    async def is_arrived(self, awb_blank = None, awb_num = None):
        url = 'https://www.moscow-cargo.com/'
        if requests.get(url).status_code != 200:
            return 'NO DATA'
        self.browser.get(url)

        awb_blank_elem = self.browser.find_element(By.CSS_SELECTOR, '[class = "awb-prefix awb-part"]')
        awb_num_elem = self.browser.find_element(By.CSS_SELECTOR, '[class = "awb-number awb-part"]')

        awb_blank_elem.send_keys(awb_blank)
        awb_num_elem.send_keys(awb_num + Keys.RETURN)
        time.sleep(3)
        status_els = self.browser.find_elements(By.CSS_SELECTOR, '[id = "statusbody"]')
        cargo_info = status_els[0].find_elements(By.TAG_NAME, "tr")[0].find_elements(By.TAG_NAME, "td")
        info = {}
        info['awb'] = cargo_info[0].text
        info['date'] = cargo_info[7].find_elements(By.TAG_NAME, "span")[1].text
        info['cw'] = cargo_info[3].find_elements(By.TAG_NAME, "div")[0].find_elements(By.TAG_NAME, "span")[1].text
        info['vol'] = cargo_info[4].text
        self.browser.close()
        return ("ARRIVED: " + info['date'], 'CW: ' + info['cw'])

        