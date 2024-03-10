import asyncio
import time
import random
import logging
import pandas as pd
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

logging.basicConfig(filemode = 'w', format='%(asctime)s - %(message)s', 
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

class PBAScraper():
    def __init__(self) -> None:
        self.pba_teams_homeurl = 'https://www.pba.ph/teams'
        self.team_dataheaders = ['Team Name','Head Coach','Manager', 'URL', 'Logo Link']
        self.pba_players_homeurl = 'https://www.pba.ph/players'
        self.player_dataheaders = ['Team Name', 'Player Name','Number', 'Position', 'URL', 'Mugshot']
        self.team_logo_image_dict = {
            'https://dashboard.pba.ph/assets/logo/converge-logo2.png':'Converge FiberXers',
            'https://dashboard.pba.ph/assets/logo/Ginebra150.png':'Barangay Ginebra San Miguel',
            'https://dashboard.pba.ph/assets/logo/Blackwater_new_logo_2021.png':'Blackwater Elite',
            'https://dashboard.pba.ph/assets/logo/GLO_web.png':'North Port Batang Pier',
            'https://dashboard.pba.ph/assets/logo/terrafirma.png':'Terrafirma Dyip',
            'https://dashboard.pba.ph/assets/logo/web_mer.png':'Meralco Bolts',
            'https://dashboard.pba.ph/assets/logo/web_nlx.png':'NLEX Road Warriors',
            'https://dashboard.pba.ph/assets/logo/web_ros.png':'Rain or Shine Elastopainters',
            'https://dashboard.pba.ph/assets/logo/SMB2020_web.png':'San Miguel Beermen',
            'https://dashboard.pba.ph/assets/logo/tropang_giga_pba.png':'TNT Tropang Giga',
            'https://dashboard.pba.ph/assets/logo/magnolia-2022-logo.png':'Magnolia Chicken Timplados Hotshots',
            'https://dashboard.pba.ph/assets/logo/viber_image_2024-03-05_17-18-02-823.png':'Phoenix Fuel Masters',
        }

        self.color_text = {
            'green':'\033[0;32m',
            'blue':'\033[0;34m',
            'cyan':'\033[0;36m',
            'red':'\033[0;31m',
            'reset':'\033[0m',
            'magenta':'\033[0;35m',
            'gray':'\033[0;37m',
            'yellow':'\033[1;33m',
            'light_purple':'\033[1;35m',
            'light_green':'\033[1;32m',
        }

    async def create_df(self, pba_type, headers):
        df = pd.DataFrame(columns=headers)
        logging.info(f"Created dataframe for {pba_type}")
        return df


    async def navigate_to_teams(self, div_number):
        attempts = 10
        for i in range(attempts):
            try:
                await self.page.goto(self.pba_teams_homeurl)
                logging.info('Navigating to PBA page...')
                # wait for the whole page to load up
                await self.page.wait_for_load_state()
                logging.info("Successfully loaded")
                time.sleep(2)
                team_selector = f'//*[contains(@id, "innity_proxy_parent_")]/div[6]/div[3]/div/div[{div_number}]'
                team_locator = await self.page.wait_for_selector(team_selector, timeout=40000)
                logging.info("Locator for a team seen")
                await team_locator.click()

            except (TimeoutError, Exception) as e:
                if i < attempts - 1:
                    logging.info(f"{self.color_text['blue']}Connection or Page problem, page will retry please wait: {e}{self.color_text['reset']}")
                    await self.page.reload()
                    await self.countdown(random.randint(1,4), "team navigation")
                    continue
                else:
                    logging.info(f"Used all {attempts} Attempts")
                    raise Exception("Page nav Needs Fixes.....")
            break

    async def navigate_to_players(self):
        attempts = 10
        for i in range(attempts):
            try:
                await self.page.goto(self.pba_players_homeurl)
                logging.info('Navigating to PBA page...')
                # wait for the whole page to load up
                await self.page.wait_for_load_state()
                logging.info("Successfully loaded")
                time.sleep(2)

            except (TimeoutError, Exception) as e:
                if i < attempts - 1:
                    logging.info(f"{self.color_text['blue']}Connection or Page problem, page will retry please wait: {e}{self.color_text['reset']}")
                    await self.page.reload()
                    await self.countdown(random.randint(1,4), "scrape player page")
                    continue
                else:
                    logging.info(f"Used all {attempts} Attempts")
                    raise Exception("Page nav Needs Fixes.....")
            break

    async def scraper_players_page(self, div_number):
        try:
            logging.info(f"{self.color_text['blue']}Player {div_number}{self.color_text['reset']}")
            logo_link_locator = await self.page.wait_for_selector(f'//*[@id="playersPool"]/div[{div_number}]/div[3]/span[2]/img', timeout=20000)
            logo_src = await logo_link_locator.evaluate('(element) => element.src')
            team_name = self.team_logo_image_dict[logo_src]
            logging.info(f"Team name: {self.color_text['magenta']}{team_name}{self.color_text['reset']}")
            player_selector = await self.page.wait_for_selector(f'//*[@id="playersPool"]/div[{div_number}]/div[2]/a/h5',timeout=30000)
            player_name = await player_selector.text_content()
            logging.info(f"Player name: {self.color_text['magenta']}{player_name}{self.color_text['reset']}")
            num_pos_locator = await self.page.wait_for_selector(f'//*[@id="playersPool"]/div[{div_number}]/div[3]/span[1]/h6',timeout=30000)
            num_pos_text = await num_pos_locator.text_content()
            number, position = [part.strip() for part in num_pos_text.split('|')]
            logging.info(f"Jersey Number: {self.color_text['magenta']}{number}{self.color_text['reset']}")
            logging.info(f"Position: {self.color_text['magenta']}{position}{self.color_text['reset']}")
            player_url_locator = await self.page.wait_for_selector(f'//*[@id="playersPool"]/div[{div_number}]/div[2]/a',timeout=30000)
            player_url = await player_url_locator.evaluate('(element) => element.href')
            logging.info(f"Player URL: {self.color_text['magenta']}{player_url}{self.color_text['reset']}")
            mugshot_locator = await self.page.wait_for_selector(f'//*[@id="playersPool"]/div[{div_number}]/div[1]/center/a/img', timeout=30000)
            mugshot_src = await mugshot_locator.evaluate('(element) => element.src')
            logging.info(f"Mugshot: {self.color_text['magenta']}{mugshot_src}{self.color_text['reset']}")

            return team_name, player_name, number, position, player_url, mugshot_src

        except (TimeoutError, Exception) as e:
            logging.info(f"Selector not found for iteration {div_number}. Error: {e}")
            return None
                


    async def scrape_team_page(self):
        """
            Implemented a retry to reload the page if a locator is not seen, or if there's page problem.
        """
        attempts = 10
        for i in range(attempts):
            try:
                await self.page.wait_for_load_state()
                logging.info("Navigated to a team page")
                team_name_locator = await self.page.wait_for_selector('//*[contains(@id, "innity_proxy_parent_")]/div[6]/div[3]/div[1]/div/div[2]/div[1]/div/h3',timeout=30000)
                team_name = await team_name_locator.text_content()
                logging.info(f"Team name: {self.color_text['magenta']}{team_name}{self.color_text['reset']}")
                head_coach_locator = await self.page.wait_for_selector('//*[contains(@id, "innity_proxy_parent_")]/div[6]/div[3]/div[1]/div/div[2]/div[2]/div[1]/h5[2]',timeout=30000)
                head_coach = await head_coach_locator.text_content()
                logging.info(f"Head coach: {self.color_text['magenta']}{head_coach}{self.color_text['reset']}")
                manager_locator = await self.page.wait_for_selector('//*[contains(@id, "innity_proxy_parent_")]/div[6]/div[3]/div[1]/div/div[2]/div[2]/div[1]/h5[4]', timeout=30000)
                manager = await manager_locator.text_content()
                logging.info(f"Manager: {self.color_text['magenta']}{manager}{self.color_text['reset']}")
                url = self.page.url
                logging.info(f"URL: {self.color_text['magenta']}{url}{self.color_text['reset']}")
                Logo_link_locator = await self.page.wait_for_selector('//*[contains(@id, "innity_proxy_parent_")]/div[6]/div[3]/div[1]/div/div[1]/center/img',timeout=30000)
                logo_src = await Logo_link_locator.evaluate('(element) => element.src')
                logging.info(f"Logo link: {self.color_text['magenta']}{logo_src}{self.color_text['reset']}")

                #going back to all teams page
                logging.info('Going back to previous all teams page')
                return team_name, head_coach, manager, url, logo_src

            except (TimeoutError, Exception) as e:
                if i < attempts - 1:
                    logging.info(f"{self.color_text['blue']}Connection or Page problem, page will retry please wait: {e}{self.color_text['reset']}")
                    await self.page.reload()
                    await self.countdown(random.randint(1,4), "scraper team page")
                    continue
                else:
                    logging.info(f"Used all {attempts} Attempts")
                    raise Exception("Page nav Needs Fixes.....")

    """ 
        randomizer delay for every bot execution.
    """
    async def wait_time(self, min_num, max_num) -> int: 
        rand_num = random.uniform(min_num,max_num)
        return rand_num

    async def countdown(self, secs, retry_message):
        for i in range(secs, 0, -1):
            logging.info(f"{self.color_text['cyan']}Retrying {retry_message} {str(i)} sec(s){self.color_text['reset']}")
            time.sleep(1)          

    async def append_to_df(self, df, data):
        if data is None:
            return df
        new_row_df = pd.DataFrame([data], columns=df.columns)
        df = pd.concat([df, new_row_df], ignore_index=True)
        logging.info("Appended tuple to dataframe")
        return df


    async def save_data_to_csv(self, title, df):
            # Generate a timestamp for the filename
            timestamp = time.strftime("%Y%m%d%H%M%S")
            # Save the DataFrame to a CSV file in the "data" folder with timestamp
            csv_filename = f"{title}_{timestamp}.csv"
            df.to_csv(f"data_pba/{csv_filename}", index=False)
            logging.info("Data saved successfully!")

    async def main(self):
        async with async_playwright() as p:
            #teams
            self.teams_df = await self.create_df('teams', self.team_dataheaders)
            self.players_df = await self.create_df('players', self.player_dataheaders)
            browser = await p.chromium.launch(slow_mo=50, headless=True)
            self.page = await browser.new_page()
            await stealth_async(self.page)
            for div_number in range(1,13):
                await self.navigate_to_teams(div_number)
                team_data = await self.scrape_team_page()
                self.teams_df = await self.append_to_df(self.teams_df, team_data)
            print(self.teams_df)
            await self.save_data_to_csv('teams',self.teams_df)

            #players
            logging.info(f"{self.color_text['cyan']} Done Scraping the Teams page! Proceeding to Players page...{self.color_text['reset']}")
            await self.navigate_to_players()
            for i in range(1,207):
                player_data = await self.scraper_players_page(i)
                self.players_df = await self.append_to_df(self.players_df, player_data)
            print(self.players_df)
            await browser.close()
            await self.save_data_to_csv('players',self.players_df)



if __name__ == '__main__':
    scraper = PBAScraper()
    asyncio.run(scraper.main())