import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
# from database.db_provider import get_db
import time
import re


class Arrival():
    def __init__(self, delay = None):
        self.base_url = "https://www.moscow-cargo.com/"
        self.browser = None
        self.page = None
        self.data = {
            'creation_date': '',
            'flight': '',
            'flight_date': '',
            'arrival_status': '',
            'cw': '',
            'from': '',
            'to': '',
        }

    async def launch_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()

    async def is_arrived(self, awb):
        flag = 1
        while flag:
            try:
                await self.launch_browser()
                await self.page.goto(self.base_url)
                awb_blank_elem = await self.page.query_selector_all('[class = "awb-prefix awb-part"]')
                awb_num_elem = await self.page.query_selector_all('[class = "awb-number awb-part"]')
                await awb_blank_elem[0].fill(awb[:3])
                await awb_num_elem[0].fill(awb[3:])
                await self.page.locator('button[id = "getstatus"]').click()
                await self.page.wait_for_selector('div[class = "modal fade bd-status_sub-lg show"]')
                is_notempty = len(await self.page.query_selector_all("span:has-text('Информации по накладной в системе нет или дата ее создания больше 90 дней')"))
                is_flight = len(await self.page.query_selector_all("td:has-text('SU')"))
                if is_notempty or not is_flight:
                    print(awb + '   ///  not arrived')
                    return 'ND'
                tbody = await self.page.query_selector('tbody[id = "statusbody"]')
                tds = await tbody.query_selector_all('td')
                self.data['creation_date'] = await tds[1].inner_text()
                self.data['flight'] = await tds[-1].inner_text()
                self.data['flight'] = re.search('.+',  self.data['flight']).group()
                self.data['flight_date'] = await tds[-1].inner_text()
                self.data['flight_date'] =  re.search('\s.+',  self.data['flight_date']).group()[1:]
                if await self.page.query_selector_all("td:has-text('Прибытие рейса')"):
                    self.data['arrival_status'] = 'ARRIVED'
                self.data['cw'] = await tds[3].inner_text()
                self.data['cw'] = re.search('\s.+',  self.data['cw']).group()[1:]
                self.data['from'] = await tds[-3].inner_text()
                self.data['to'] = await tds[-2].inner_text()
                flag = 0
                return self.data
            except Exception as e:
                print(e)
                print('another attempt for //' + awb)
                pass
        # return str(await tds[].inner_text()).replace("\n", "/")

        
# if __name__ == '__main__':
#     ar = Arrival()
#     print(asyncio.run(ar.is_arrived('555-10216673')))