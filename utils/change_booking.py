from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import os
from dotenv import load_dotenv
import time
import asyncio
load_dotenv()

LOGIN = os.getenv('LOGIN_TR')
PASS = os.getenv('PASS_TR')

class Change_booking():
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--no-sandbox')
        # self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(self.chrome_options)

    async def change(self, awb, fr = None, to = None, pcs = None, w = None, v = None, cargo = None, flight = None, day = None, month = None, message = None):
        url = 'https://afl.booking-cargo.ru/waybills'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        time.sleep(.5)
        # time.sleep(1)
        # self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-horizontal ant-space-align-center ant-space-gap-row-small ant-space-gap-col-small"]').click()
        # time.sleep(.1)
        # self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-dropdown-menu-title-content"]')[1].click()
        # await message.answer("Authorizing...")
        login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
        pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
        login_el.send_keys(LOGIN)
        pass_el.send_keys(PASS, Keys.ENTER)
        time.sleep(2)
        self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-picker-clear"]').click()
        time.sleep(2)
        booked_flights_els = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
        for i in range(len(booked_flights_els)):
            booked_flight = booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].text
            if booked_flight == awb:
                booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].click()
                break
        time.sleep(4)
        #старый букинг
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        await message.answer("Previous booking status:  " + '<b>' +  booking_status + '</b>')
        self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-circle ant-btn-text ant-btn-color-default ant-btn-variant-text ant-btn-sm ant-btn-icon-only"]')[2].click()
        time.sleep(2)
        new_booking_els = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]').find_elements(By.TAG_NAME, "input")
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        time.sleep(.2)
        new_booking_els[0].send_keys(Keys.DELETE)
        new_booking_els[0].send_keys(pcs)

        new_booking_els[1].send_keys(Keys.COMMAND+"a")
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        time.sleep(.2)
        new_booking_els[1].send_keys(Keys.DELETE)
        new_booking_els[1].send_keys(w)

        new_booking_els[2].send_keys(Keys.COMMAND+"a")
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        time.sleep(.2)
        new_booking_els[2].send_keys(Keys.DELETE)
        new_booking_els[2].send_keys(v)

        time.sleep(1)
        self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]').find_element(By.TAG_NAME, "button").click()
        #новый букинг
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-circle ant-btn-text ant-btn-color-default ant-btn-variant-text ant-btn-sm ant-btn-icon-only"]')[3].click()
        time.sleep(5)
        self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")[2].click()
        time.sleep(1)
        time.sleep(.5)
        flag = True
        while(flag):
            time.sleep(.5)
            flights_els = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-table-wrapper TableBookingFlight__TableStyled-gHCKPF ksiLWd css-lked6w"]').find_elements(By.TAG_NAME, "tr")
            for i in range(2, len(flights_els)):
                if flights_els[i].find_elements(By.TAG_NAME, "td")[2].text[:2] == day and flights_els[i].find_elements(By.TAG_NAME, "td")[3].text[2:6] == flight:
                    flights_els[i].find_elements(By.TAG_NAME, "td")[0].click()
                    flag = False
                    break
            try:
                self.browser.find_elements(By.CSS_SELECTOR, '[title = "Вперед"]')[0].click()
            except:
                pass
        time.sleep(.2)
        self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")[0].click()
        time.sleep(.2)
        self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")[3].click()
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        await message.answer("New booking status:  " + '<b>' +  booking_status + '</b>')
        awb_actual = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-select-selector"]')[3].text
        flight_actual = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm ButtonLink__ButtonStyled-eeryZM gvPyWL"]').text
        ffa = f"""FFA/4
        {awb_actual}{fr}{to}/T{pcs}K{w}MC{v}/{cargo}
        {flight_actual}/{day}{month}/{fr}{to}/{booking_status}
        REF/CHACSSU"""
        await message.answer(ffa)
        self.browser.close()


    async def cancel(self, awb):
        url = 'https://afl.booking-cargo.ru/waybills'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        time.sleep(.5)
        # time.sleep(1)
        # self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-horizontal ant-space-align-center ant-space-gap-row-small ant-space-gap-col-small"]').click()
        # time.sleep(.1)
        # self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-dropdown-menu-title-content"]')[1].click()
        # await message.answer("Authorizing...")
        login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
        pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
        login_el.send_keys(LOGIN)
        pass_el.send_keys(PASS, Keys.ENTER)
        time.sleep(2)
        self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-picker-clear"]').click()
        time.sleep(2)
        booked_flights_els = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
        for i in range(len(booked_flights_els)):
            booked_flight = booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].text
            if booked_flight == awb:
                booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].click()
                break
        time.sleep(4)
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        if booking_status != "CN":
            self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-default ant-btn-dangerous ant-btn-color-dangerous ant-btn-variant-outlined ant-btn-sm"]').click()
        time.sleep(1)
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        print(booking_status)
        self.browser.close()

if __name__ == "__main__":
    ch = Change_booking()
    asyncio.run(ch.change('555-10216813', pcs="2", w="24", v = "0.05", day= "23", month="MAR", flight="2139"))
    # asyncio.run(ch.cancel('555-10216813'))


