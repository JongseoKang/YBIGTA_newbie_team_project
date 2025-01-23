from tqdm import tqdm
from typing import Any
from base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import pandas as pd
import json
import os
import sys
from time import sleep


class JSCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.output_dir = os.path.join(output_dir, "reviews_Megabox.csv")
        self.review_list:list[str] = []
        self.rating_list:list[str] = []
        self.date_list:list[datetime] = []
        self.driver:webdriver.Chrome = webdriver.Chrome()
        self.url = f'https://www.megabox.co.kr/movie-detail/comment?rpstMovieNo=25000200'

    def start_browser(self) -> None:
        '''start chrome browser'''
        driver:webdriver.Chrome = self.driver
        driver.maximize_window()
        driver.get(self.url)
        sleep(3)

    def scrape_reviews(self) -> list[dict[str, Any]]:
        """Scrape reviews from the specified URL."""
        self.start_browser()
        browser = self.browser
        
        url = 'https://www.google.com/maps/place/%EC%95%A0%ED%94%8C+%ED%8C%8C%ED%81%AC/@37.3346434,-122.0192503,15z/data=!3m1!4b1!4m6!3m5!1s0x808fb596e9e188fd:0x3b0d8391510688f0!8m2!3d37.3346438!4d-122.008972!16s%2Fg%2F11bzx2n6td?entry=ttu&g_ep=EgoyMDI1MDExNS4wIKXMDSoASAFQAw%3D%3D'
        browser.get(url)
        sleep(3)
        reviews =[]
        
        # 리뷰 더보기로 이동
        more_btn=browser.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]')
        more_btn.click()
        sleep(3)
        
        # div태그 스크롤 
        js_scripts = '''
        let aa = document.getElementsByClassName('section-scrollbox')[0];
        aa.scrollBy(0,10000);
        '''
        browser.execute_script(js_scripts)
        sleep(3) 
        
        # 헤더값 찾기
        for request in browser.requests:
            if request.response:
                pb=request.url.split('pb=')
                if len(pb)==2:
                    if pb[1][:6]=='!1m2!1':
                        url_l=request.url.split('!2m2!1i')
                        break       

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
                    dateVal:str = date[0].text
                    result:datetime = datetime.now()
                    if dateVal.endswith("지금"):
                        result = datetime.now()
                    elif dateVal.endswith(" 분전"):
                        result = datetime.now() - timedelta(minutes=float(dateVal[:-3]))
                    elif dateVal.endswith(" 시간전"):
                        result = datetime.now() - timedelta(hours=float(dateVal[:-4]))
                    elif dateVal.endswith(" 일전"):
                        result = datetime.now() - timedelta(days=float(dateVal[:-3]))
                    date_list.append(result)
                else:
                    date_list.append(datetime(0, 0, 0))
            next = 0
            if i <= 10:
                next = i
            elif i % 10 == 0:
                next = 12
            else:
                next = i % 10 + 2
            driver.find_element(By.XPATH, f'//*[@id="contentData"]/div/div[4]/nav/a[{next}]').click()
            sleep(2)


    def save_to_database(self) -> None:
        """Save reviews."""
        df=pd.DataFrame(self.reviews)
        df.to_csv(os.path.join(self.output_dir, "reviews_Google.csv"))

    def close_browser(self) -> None:
        """Close the Selenium WebDriver."""
        if self.browser:
            self.browser.quit()
            self.browser = None
