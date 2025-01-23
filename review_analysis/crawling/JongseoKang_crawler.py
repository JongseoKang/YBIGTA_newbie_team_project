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
        self.output_dir = output_dir
        self.browser: webdriver.Chrome | None = None

    def start_browser(self) -> None:
        """Initialize the Selenium WebDriver."""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('disable-gpu')
        # chrome_options.add_argument('headless')
        self.browser = webdriver.Chrome(options=chrome_options)
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

        for number in tqdm(range(300)):
            resp=requests.get((url_l[0]+'!2m2!1i'+'{}'+url_l[1]).format(number))
            review = json.loads(resp.text[5:])
            for user in range(10):
                reviews.append({
                    '리뷰':review[2][user][3],
                    '날짜':review[2][user][1],
                    '별점':review[2][user][4]})
        
        self.reviews = review


    def save_to_database(self) -> None:
        """Save reviews."""
        df=pd.DataFrame(self.reviews)
        df.to_csv(os.path.join(self.output_dir, "reviews_Google.csv"))

    def close_browser(self) -> None:
        """Close the Selenium WebDriver."""
        if self.browser:
            self.browser.quit()
            self.browser = None
