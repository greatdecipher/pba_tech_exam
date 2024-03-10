import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

class PBAScraper():
    def __init__(self) -> None:
        self.pba_teams_homeurl = 'https://www.pba.ph/teams'
        self.pba_players_homeurl = 'https://www.pba.ph/players'

    async def navigate_to_site(self, url):
        await self.page.goto(url)
        print('Navigating to PBA page...')
        # wait for the whole page to load up
        await self.page.wait_for_load_state()
        print("Successfully loaded")
        



    async def main(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(slow_mo=50, headless=False)
            self.page = await browser.new_page()
            await stealth_async(self.page)
            await self.navigate_to_site(self.pba_teams_homeurl)
            await browser.close()



if __name__ == '__main__':
    scraper = PBAScraper()
    asyncio.run(scraper.main())