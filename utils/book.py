from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()

LOGIN = os.getenv('LOGIN_TR')
PASS = os.getenv('PASS_TR')

class Booking():
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(self.chrome_options)

    async def book(self, awb, fr = None, to = None, pcs = None, w = None, v = None, cargo = None, flight = None, day = None, month = None, message = None):
        url = 'https://afl.booking-cargo.ru/'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        time.sleep(1)
        self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-horizontal ant-space-align-center ant-space-gap-row-small ant-space-gap-col-small"]').click()
        time.sleep(.1)
        self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-dropdown-menu-title-content"]')[1].click()
        await message.answer("Authorizing...")
        login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
        pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
        login_el.send_keys(LOGIN)
        pass_el.send_keys(PASS, Keys.ENTER)
        time.sleep(1)

        book_el1 = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-col ant-col-4 css-lked6w"]')
        book_el1.click()
        time.sleep(3)
        await message.answer("Filling up the booking details...")

        awb_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[5]
        # awb_input_el.send_keys("555-", awb, Keys.ENTER)
        awb_input_el.send_keys(Keys.ENTER, Keys.ENTER)
        awb_actual = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-select-selector"]')[3].text
        time.sleep(1)
        from_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[8]
        from_input_el.send_keys(fr, Keys.ENTER)
        to_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[9]
        to_input_el.send_keys(to, Keys.ENTER)
        pcs_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[11]
        pcs_input_el.send_keys(pcs, Keys.ENTER)
        weight_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[13]
        weight_input_el.send_keys(w, Keys.ENTER)
        vol_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[15]
        vol_input_el.send_keys(v, Keys.ENTER)
        cargo_input_el = self.browser.find_elements(By.TAG_NAME, 'textarea')[0]
        cargo_input_el.send_keys(cargo, Keys.ENTER)
        choose_flight_el = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm FormFlightBuilder__ButtonPickFlights-hFgekQ SOGsx"]')
        choose_flight_el.click()
        time.sleep(1)

        next_pg_elem = self.browser.find_element(By.CSS_SELECTOR, '[class = "anticon anticon-right"]')
        flag = True
        await message.answer("Confirming...")
        while (flag):
            flight_elems = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
            for flight_info in flight_elems:
                td_elems = flight_info.find_elements(By.TAG_NAME, "td")
                flightnum_elem = td_elems[3]
                if flightnum_elem.text[2:] == flight and td_elems[2].text[:2] == day:
                    td_elems[0].click()
                    flag = False
                    break
            try:
                next_pg_elem.click()
                time.sleep(1)
            except:
                continue
        time.sleep(.5)
        apply_el = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-primary ant-btn-color-primary ant-btn-variant-solid ant-btn-sm"]')
        apply_el.click()
        time.sleep(.5)
        confirm_el = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-primary ant-btn-color-primary ant-btn-variant-solid"]')[1]
        confirm_el.click()
        await message.answer("Your awb number is: " + awb_actual)
        time.sleep(.5)
        self.browser.execute_script("window.scrollTo(100, 100)")
        self.browser.save_screenshot("555-"+awb+".png")
        self.browser.close()

            
if __name__ == '__main__':
    bk = Booking()
    bk.book('04896474', "LED", "SVO", 3, 34, '0.2', "SPP", "6519", "13")