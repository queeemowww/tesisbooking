from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import asyncio
import time
from openpyxl import load_workbook

class Track():
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--no-sandbox')
        # self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(self.chrome_options)

    async def track_svo(self, awb_blank = None, awb_num = None):
        url = 'https://www.moscow-cargo.com/'
        
        if requests.get(url).status_code != 200:
            return 'В данный момент трекинг недоступен. Попробуйте позднее'
        self.browser.get(url)

        awb_blank_elem = self.browser.find_element(By.CSS_SELECTOR, '[class = "awb-prefix awb-part"]')
        awb_num_elem = self.browser.find_element(By.CSS_SELECTOR, '[class = "awb-number awb-part"]')

        awb_blank_elem.send_keys(awb_blank)
        awb_num_elem.send_keys(awb_num + Keys.RETURN)

        time.sleep(2)
        try:
            status_els = self.browser.find_elements(By.CSS_SELECTOR, '[id = "status"]')
            cargo_info = []
            for i in range(len(status_els[0].find_elements(By.TAG_NAME, "tr"))):
                cargo_info.append(status_els[0].find_elements(By.TAG_NAME, "tr")[i].text)
            return cargo_info
        except Exception as e:
            print(e)
            return 'Не удалось найти накладную с номером ' + '<code>' + awb_blank + '-' + awb_num + '</code>'
        finally:
            self.browser.close()
            
async def main():
    tr = Track()
    a = await (tr.track_svo("555", "08392230"))
    print(a)
asyncio.run(main())