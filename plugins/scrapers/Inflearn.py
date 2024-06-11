import time
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pymysql
from sqlalchemy import create_engine

# Configure Selenium
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

SUBCATEGORY_FILE_PATH = '/Users/leehah/OnlineClass_Project/files/inflearn_subcategories.json'

# Inflearn URL
BASE_URL = 'https://www.inflearn.com/courses/'

# MySQL
DATABASE_TYPE = 'mysql'
DBAPI = 'mysqlconnector'
ENDPOINT = 'localhost'
USER = 'leehah'
PASSWORD = 'leehah'
PORT = 3306
DATABASE = 'OnlineClass'


def current_page_crawling(soup):
    raw_title = soup.find_all(class_='mantine-Text-root css-10bh5qj mantine-169r75g')
    raw_instructor = soup.select('#__next > main > div > section.css-18qnvtf.mantine-1avyp1d > ul > li > a > article > div.css-13udsys.mantine-5t8g7z > div.css-17cnqmk.mantine-5n4x4z > p.mantine-Text-root.css-1r49xhh.mantine-17j39m6')
    raw_url = soup.select('#__next > main > div > section.css-18qnvtf.mantine-1avyp1d > ul > li > a')
    raw_price = soup.find_all(class_='mantine-Text-root css-uzjboo mantine-nu4660')
    raw_detail = soup.find_all(class_='mantine-Text-root css-1uons5e mantine-z3c1iu')
    raw_img = soup.find_all(class_='mantine-AspectRatio-root css-2oqlco mantine-1w8yksd')
    
    title = [i.text for i in raw_title]
    instructor = [i.text for i in raw_instructor]
    url = [i['href'] for i in raw_url]
    price = [i.text for i in raw_price]
    detail = [i.text for i in raw_detail]
    img = [i.find('img')['src'] if i.find('img') else '' for i in raw_img]

    df = pd.DataFrame({"title" : title,
                       "instructor" : instructor,
                       "url" : url,
                       "price" : price,
                       "detail" : detail,
                       "img" : img})
    
    return df

def fetch_all_courses():
    all_data = pd.DataFrame()

    with open(SUBCATEGORY_FILE_PATH, 'r') as f:
        subcategory_list = json.load(f)

    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

    for subcategory in subcategory_list:
        driver.get(f"{BASE_URL}{subcategory}")
        max_page = int(driver.find_elements(By.XPATH, '//*[@id="__next"]/main/div/div/div/button')[-2].text)

        for current_page in range(1, max_page + 1):
            driver.get(f"{BASE_URL}{subcategory}?page_number={current_page}")
            driver.implicitly_wait(5)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            df = current_page_crawling(soup)
            df['sub_category'] = subcategory
            all_data = pd.concat([all_data, df], ignore_index = True)
    
    driver.quit()

    return all_data


def main():
    all_data = fetch_all_courses()
    print(f"Total courses fetched: {len(all_data)}")

    try:
        db_connection_str = f'{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}'
        db_connection = create_engine(db_connection_str)
        conn = db_connection.connect()

        all_data.to_sql(name = 'inflearn_class_list',
                                        con = db_connection,
                                        if_exists = 'append',
                                        index = False
                                    )
        print("Data stored in MySQL successfully")
        conn.close()
        
    except Exception as e:
        conn.close()
        print(e)

if __name__ == '__main__':
    main()