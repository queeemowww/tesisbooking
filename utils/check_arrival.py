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

    async def launch_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()

    async def is_arrived(self, awb):
        await self.launch_browser()
        await self.page.goto(self.base_url)
        awb_blank_elem = await self.page.query_selector_all('[class = "awb-prefix awb-part"]')
        awb_num_elem = await self.page.query_selector_all('[class = "awb-number awb-part"]')
        await awb_blank_elem[0].fill(awb[:3])
        await awb_num_elem[0].fill(awb[3:])
        await self.page.locator('button[id = "getstatus"]').click()
        await self.page.wait_for_selector('div[class = "modal fade bd-status_sub-lg show"]')
        tbody = await self.page.query_selector('tbody[id = "statusbody"]')
        tds = await tbody.query_selector_all('td')
        if len(tds) <= 2:
            return 'ND'
        return str(await tds[-1].inner_text()).replace("\n", "/")

        
# if __name__ == '__main__':
#     ar = Arrival()
#     print(asyncio.run(ar.is_arrived('555-01312313')))