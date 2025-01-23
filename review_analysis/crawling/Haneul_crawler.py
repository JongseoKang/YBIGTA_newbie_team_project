# 모듈 임포트
import sys
import time
import os

from review_analysis.crawling.base_crawler import BaseCrawler

# 셀레니움 관련
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

# 크롬 드라이버 자동설치를 위한 라이브러리
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# 판다스(데이터 저장용)
import pandas as pd

class HNCrawler(BaseCrawler):
    """
    A crawler class that scrapes movie reviews from Naver's search pages using Selenium.
    Inherits from BaseCrawler to ensure consistent interface (scrape_reviews, save_to_database, etc.).
    """

    def __init__(self, output_dir: str) -> None:
        """
        Initialize the HNCrawler with the base URL, and set up internal variables.

        Args:
            output_dir (str): The directory path where scraped data will be saved as a CSV file.
        """
        super().__init__(output_dir)

        # Example: The movie name to be searched/crawled
        self.movie_name: str = '히트맨2'

        # Construct the base URL using the movie name
        self.base_url: str = (
            f"https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&mra=bkEw&pkid=68&os=33549337&qvt=0&query={self.movie_name}%20%EA%B4%80%EB%9E%8C%ED%8F%89"
        )

        # Selenium driver will be stored here after start_browser()
        self.driver: webdriver.Chrome | None = None

        # A list of dictionaries, each representing one review
        self.data: list[dict[str, str]] = []

        # Additional info
        self.released_date: str = ""
        self.movie_title: str = ""

    def start_browser(self) -> None:
        """
        Start the Chrome WebDriver using webdriver_manager for automatic installation,
        navigate to the base URL, and gather initial information such as released date and movie title.

        """
        # Start Chrome driver
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install())
        )

        # 1) Navigate to the base page
        self.driver.get(self.base_url)

        # 2) Fetch released date
        raw_released_date = self.driver.find_elements(
            By.XPATH, '/html/body/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[2]/div/div[1]/dl/div[2]/dd'
        )
        if raw_released_date:
            self.released_date = raw_released_date[0].text
            print("개봉일:", self.released_date)

        # 3) Navigate to reviews page
        self.driver.get(
            f'https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&mra=bkEw&pkid=68&os=33549337&qvt=0&query={self.movie_name}%20%EA%B4%80%EB%9E%8C%ED%8F%89'
        )
        time.sleep(1)

        # 4) Fetch movie title
        raw_movie_title = self.driver.find_elements(
            By.XPATH, '/html/body/div[3]/div[2]/div[1]/div[1]/div[3]/div[1]/div[1]/h2/span/strong'
        )
        if raw_movie_title:
            self.movie_title = raw_movie_title[0].text
            print("영화 제목:", self.movie_title)
        time.sleep(0.5)

    def scrape_reviews(self) -> None:
        """
        Main method to start the browser (if not already started),
        scroll through the page, and scrape the reviews, star ratings, and writing dates.
        The scraped data is stored in the self.data list.

        """
        # 1) Start Selenium if not done yet
        self.start_browser()

        # 2) Initial scroll
        if self.driver:
            ActionChains(self.driver).scroll_by_amount(0, 600).perform()
        time.sleep(1)

        # Debug/confirm
        print("[스크레이핑 시작]")
        print("영화 제목:", self.movie_title)
        print("개봉 일자:", self.released_date)

        if not self.driver:
            print("Driver not initialized. Aborting scrape.")
            return

        scroll_origin = ScrollOrigin.from_viewport(140, 641)
        crawl_rounds: int = 100
        comment_index: int = 1

        for round_idx in range(crawl_rounds):
            print(f"\n=== [라운드 {round_idx + 1}/{crawl_rounds}] 리뷰 5개 크롤링 시작 ===\n")
            no_more_reviews: bool = False

            for _ in range(5):
                # 1) 리뷰 코멘트
                try:
                    xpath_comment = (
                        f"/html/body/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div/div/div[4]/div[4]/ul/li[{comment_index}]/div[2]/div/span[2]"
                    )
                    raw_comment = self.driver.find_elements(By.XPATH, xpath_comment)
                except Exception as e:
                    print(f"Selector 예외 발생(코멘트 부분): {e}")
                    no_more_reviews = True
                    break

                # 더 이상 리뷰가 없는 경우
                if not raw_comment:
                    print(f"[종료] li[{comment_index}] (코멘트) 없음 → 더 이상 리뷰가 없다고 판단.")
                    no_more_reviews = True
                    break
                comment: str = raw_comment[0].text

                # 2) 별점
                try:
                    xpath_star = (
                        f"/html/body/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div/div/div[4]/div[4]/ul/li[{comment_index}]/div[1]/div/div[2]"
                    )
                    raw_star_score = self.driver.find_elements(By.XPATH, xpath_star)
                    star_score: str = raw_star_score[0].text if raw_star_score else ""
                    star_score = star_score.split("\n")[-1]
                except Exception as e:
                    print(f"Selector 예외 발생(별점 부분): {e}")
                    star_score = ""

                # 3) 작성일
                try:
                    xpath_date = (
                        f"/html/body/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div/div/div[4]/div[4]/ul/li[{comment_index}]/dl/dd[2]"
                    )
                    raw_writing_date = self.driver.find_elements(By.XPATH, xpath_date)
                    writing_date: str = raw_writing_date[0].text if raw_writing_date else ""
                except Exception as e:
                    print(f"Selector 예외 발생(작성일 부분): {e}")
                    writing_date = ""

                # 데이터 리스트에 저장
                self.data.append({
                    "영화 제목": self.movie_title,
                    "review": comment,
                    "rating": star_score,
                    "date": writing_date
                })

                # 콘솔 출력
                print(f"[리뷰 #{comment_index}] 작성일: {writing_date}, 별점: {star_score}")
                print("감상평:", comment)

                comment_index += 1
                time.sleep(0.5)

            if no_more_reviews:
                print("\n[더 이상 리뷰가 없어 라운드 중단]\n")
                break

            # 5개(한 라운드) 끝난 후 스크롤
            print(f"\n=== [라운드 {round_idx + 1}] 종료: 1000px 스크롤 내립니다. ===\n")
            ActionChains(self.driver).scroll_from_origin(scroll_origin, 0, 1000).perform()
            time.sleep(3)

        print("\n[모든 크롤링 작업 종료]\n")

    def save_to_database(self) -> None:
        """
        Save the scraped data (self.data) into a CSV file within the output directory.

        """
        if not self.data:
            print("No data to save.")
            return

        df = pd.DataFrame(self.data)
        # output_dir 밑에 CSV 파일 이름 설정
        output_file: str = os.path.join(self.output_dir, "reviews_NaverMovie.csv")
        df.to_csv(output_file, index=False, encoding="utf-8-sig")

        print(f"크롤링 데이터를 '{output_file}'에 저장했습니다.")

        # 드라이버 정리
        if self.driver:
            self.driver.quit()