from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import os
from dotenv import load_dotenv
import time
from db import Db
load_dotenv()

database = Db()
prev = {}

ADMIN_ID = os.getenv('ADMIN_ID')
LOGIN_TR = os.getenv('LOGIN_TR')
PASS_TR = os.getenv('PASS_TR')

LOGIN_CN = os.getenv('LOGIN_CN')
PASS_CN = os.getenv('PASS_CN')

class Booking():
    def __init__(self, country):
        if country == "TURKEY":
            self.login = LOGIN_TR
            self.password = PASS_TR
        if country == "CHINA":
            self.login = LOGIN_CN
            self.password = PASS_CN

        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--no-sandbox')
        # self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(self.chrome_options)

    async def book(self, awb = None, fr = None, to = None, pcs = None, w = None, v = None, cargo = None, flight = None, day = None, month = None, message = None):
        url = 'https://afl.booking-cargo.ru/'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        prev[message.chat.id] = await message.answer("Authorizing...")
        time.sleep(1.5)
        login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
        pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
        login_el.send_keys(self.login)
        pass_el.send_keys(self.password, Keys.ENTER)
        time.sleep(1.5)

        book_el1 = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-col ant-col-4 css-lked6w"]')
        book_el1.click()
        time.sleep(3)
        prev[message.chat.id].delete()
        prev[message.chat.id] = await message.answer("Filling up the booking details...")

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
        time.sleep(.5)
        choose_flight_el = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm FormFlightBuilder__ButtonPickFlights-hFgekQ SOGsx"]')
        choose_flight_el.click()
        time.sleep(2)

        next_pg_elem = self.browser.find_element(By.CSS_SELECTOR, '[class = "anticon anticon-right"]')
        flag = True
        prev[message.chat.id].delete()
        prev[message.chat.id] = await message.answer("Confirming...")
        while (flag):
            flight_elems = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
            for flight_info in flight_elems:
                td_elems = flight_info.find_elements(By.TAG_NAME, "td")
                flightnum_elem = td_elems[3]
                if flightnum_elem.text.lower() == flight.lower() and td_elems[2].text[:2] == day:
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
        prev[message.chat.id].delete()
        prev[message.chat.id] = await message.answer("Your awb number is: " + awb_actual)
        time.sleep(3)
        flight_actual = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm ButtonLink__ButtonStyled-eeryZM gvPyWL"]').text
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        ffa = f"""FFA/4
{awb_actual}{fr}{to}/T{pcs}K{w}MC{v}/{cargo}
{flight_actual}/{day}{month}/{fr}{to}/{booking_status}
REF/CHACSSU""".upper()
        prev[message.chat.id].delete()
        await message.answer('<code>' + ffa + '</code>')
        database.insert_awb(awb_actual, flight_actual, day+month.upper(), booking_status, 'NO DATA', message.chat.id)
        await message.bot.send_message(chat_id=ADMIN_ID, text = f'{message.chat.full_name}:<code>{ffa}</code>')
        del prev[message.chat.id]
        self.browser.close()

    async def change(self, awb, fr = None, to = None, pcs = None, w = None, v = None, cargo = None, flight = None, day = None, month = None, message = None):
        prev = {}
        url = 'https://afl.booking-cargo.ru/waybills'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        time.sleep(1)
        prev[message.chat.id] = await message.answer("Authorizing...")
        login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
        pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
        login_el.send_keys(self.login)
        pass_el.send_keys(self.password, Keys.ENTER)
        time.sleep(2)
        self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-picker-clear"]').click()
        time.sleep(3)
        booked_flights_els = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
        for i in range(len(booked_flights_els)):
            booked_flight = booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].text
            if booked_flight == awb:
                booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].click()
                break
        time.sleep(5)
        #старый букинг
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        prev[message.chat.id].delete()
        prev[message.chat.id] = await message.answer("Filling up new cargo details...")
        await message.answer("Previous booking status:  " + '<b>' +  booking_status + '</b>')
        time.sleep(1)
        self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-circle ant-btn-text ant-btn-color-default ant-btn-variant-text ant-btn-sm ant-btn-icon-only"]')[2].click()
        time.sleep(2)
        new_booking_els = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]').find_elements(By.TAG_NAME, "input")
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        time.sleep(.5)
        new_booking_els[0].send_keys(Keys.DELETE)
        new_booking_els[0].send_keys(pcs)

        new_booking_els[1].send_keys(Keys.COMMAND+"a")
        new_booking_els[1].send_keys(Keys.COMMAND+"a")
        new_booking_els[1].send_keys(Keys.COMMAND+"a")
        time.sleep(.5)
        new_booking_els[1].send_keys(Keys.DELETE)
        new_booking_els[1].send_keys(w)

        new_booking_els[2].send_keys(Keys.COMMAND+"a")
        new_booking_els[2].send_keys(Keys.COMMAND+"a")
        new_booking_els[2].send_keys(Keys.COMMAND+"a")
        time.sleep(.5)
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
        prev[message.chat.id].delete()
        prev[message.chat.id] = await message.answer("Searching for new flight...")
        flag = True
        while(flag):
            time.sleep(1)
            flights_els = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-table-wrapper TableBookingFlight__TableStyled-gHCKPF ksiLWd css-lked6w"]').find_elements(By.TAG_NAME, "tr")
            for i in range(2, len(flights_els)):
                if flights_els[i].find_elements(By.TAG_NAME, "td")[2].text[:2] == day and flights_els[i].find_elements(By.TAG_NAME, "td")[3].text.lower() == flight.lower():
                    flights_els[i].find_elements(By.TAG_NAME, "td")[0].click()
                    flag = False
                    break
            try:
                self.browser.find_elements(By.CSS_SELECTOR, '[title = "Вперед"]')[0].click()
            except:
                pass
        time.sleep(1)
        self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")[0].click()
        time.sleep(1)
        self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")[3].click()
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        prev[message.chat.id].delete()
        prev[message.chat.id] = await message.answer("New booking status:  " + '<b>' +  booking_status + '</b>')
        awb_actual = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-select-selector"]')[3].text
        time.sleep(1)
        flight_actual = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm ButtonLink__ButtonStyled-eeryZM gvPyWL"]').text
        ffa = f"""FFA/4
{awb}{fr}{to}/T{pcs}K{w}MC{v}/{cargo}
{flight_actual}/{day}{month}/{fr}{to}/{booking_status}
REF/CHACSSU""".upper()
        prev[message.chat.id].delete()
        await message.answer('<code>' + ffa + '</code>')
        database.update_awb(awb, ['booking_status', booking_status])
        database.update_awb(awb, ['flight', flight_actual])
        database.update_awb(awb, ['date', day+month.upper()])
        await message.bot.send_message(chat_id=ADMIN_ID, text = f'{message.chat.full_name}:<code>{ffa}</code>')
        del prev[message.chat.id]
        self.browser.close()

    async def cancel(self, awb, message):
        url = 'https://afl.booking-cargo.ru/waybills'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        time.sleep(1)
        prev[message.chat.id] = await message.answer("Authorizing...")
        login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
        pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
        login_el.send_keys(self.login)
        pass_el.send_keys(self.password, Keys.ENTER)
        time.sleep(10)
        self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-picker-clear"]').click()
        time.sleep(5)
        booked_flights_els = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
        prev[message.chat.id].delete()
        prev[message.chat.id] = await message.answer(f"Searching for {awb}...")
        for i in range(len(booked_flights_els)):
            booked_flight = booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].text
            if booked_flight == awb:
                booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].click()
                prev[message.chat.id] = await message.answer(f"Found {awb}")
                break
        time.sleep(10)
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        if booking_status != "CN":
            self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-default ant-btn-dangerous ant-btn-color-dangerous ant-btn-variant-outlined ant-btn-sm"]').click()
        time.sleep(1)
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        prev[message.chat.id].delete()
        database.update_awb(awb, ['booking_status', booking_status])
        await message.answer(f"{awb}:  " + '<b>' +  booking_status + '</b>')
        self.browser.close()

    async def check(self, awb, message):
        url = 'https://afl.booking-cargo.ru/waybills'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        time.sleep(1)
        prev[message.chat.id] = await message.answer("Authorizing...")
        login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
        pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
        login_el.send_keys(self.login)
        pass_el.send_keys(self.password, Keys.ENTER)
        time.sleep(5)
        self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-picker-clear"]').click()
        time.sleep(3)
        booked_flights_els = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
        for i in range(len(booked_flights_els)):
            booked_flight = booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].text
            if booked_flight == awb:
                booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].click()
                break
        time.sleep(10)
        #старый букинг
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        prev[message.chat.id].delete()
        database.update_awb(awb, ['booking_status', booking_status])
        await message.answer(f"{awb}:  " + '<b>' +  booking_status + '</b>')
        self.browser.close()

# if __name__ == '__main__':
#     bk = Booking()
#     bk.change('555-10217126', "ist", "SVO", 10, 10, '0.2', "SPP", "SU2139", "")