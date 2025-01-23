import requests as re
from bs4 import BeautifulSoup as bs
import pandas as pd 
import os
from base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta

from time import sleep

class JSCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        '''Constructor for JSCrawler'''
        super().__init__(output_dir)
        self.output_dir = os.path.join(output_dir, "review_Megabox.csv")
        self.review_list = []
        self.rating_list = []
        self.date_list = []
        self.driver = None
        self.url = f'https://www.megabox.co.kr/movie-detail/comment?rpstMovieNo=25000200'

    
    def start_browser(self) -> None:
        '''start chrome browser'''
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(self.url)
        sleep(3)
        self.driver = driver

    def scrape_reviews(self) -> None:
        """Scrape reviews from the specified URL."""

        self.start_browser()
        driver = self.driver
        text_list = []
        rating_list = []
        date_list = []

        for i in range(1, 101):
            html = driver.page_source
            soup = bs(html, 'html.parser')
            for j in range(2, 12):
                main_selector = f'#contentData > div > div.movie-idv-story > ul > li:nth-child({j})'
                
                #contentData > div > div.movie-idv-story > ul > li:nth-child(2) 
                text_selector = f'{main_selector} > div.story-area > div.story-box > div > div.story-cont > div.story-txt'
                text = soup.select(text_selector)
                if text:
                    text_list.append(text[0].text)
                else:
                    text_list.append("")
                
                rating_selector= f'{main_selector} > div.story-area > div.story-box > div > div.story-cont > div.story-point > span'
                rating = soup.select(rating_selector)
                if rating:
                    rating_list.append(rating[0].text)
                else:
                    rating_list.append("")
                
                date_selector = f'{main_selector} > div.story-date > div > span'
                date = soup.select(date_selector)
                if date:
                    dateVal = date[0].text
                    if dateVal.endswith("지금"):
                        dateVal = datetime.now()
                    elif dateVal.endswith(" 분전"):
                        dateVal = datetime.now() - timedelta(minutes=float(dateVal[:-3]))
                    elif dateVal.endswith(" 시간전"):
                        dateVal = datetime.now() - timedelta(hours=float(dateVal[:-4]))
                    elif dateVal.endswith(" 일전"):
                        dateVal = datetime.now() - timedelta(days=float(dateVal[:-3]))
                    else:
                        dateVal = ""
                    date_list.append(dateVal)
                else:
                    date_list.append("")
            next = 0
            if i <= 10:
                next = i
            elif i % 10 == 0:
                next = 12
            else:
                next = i % 10 + 2
            driver.find_element(By.XPATH, f'//*[@id="contentData"]/div/div[4]/nav/a[{next}]').click()
            sleep(2)


        self.rating_list = rating_list
        self.date_list = date_list
        self.review_list = text_list
            

    def save_to_database(self) -> None:
        """Save reviews."""
        review_df = pd.DataFrame(columns = ['review', 'rating', 'date'])
        review_df['review'] = self.review_list
        review_df['rating'] = self.rating_list
        review_df['date'] = self.date_list
        review_df.to_csv(self.output_dir)
