import requests
import json
import pandas as pd
import pymysql
from sqlalchemy import create_engine

SUBCATEGORY_FILE_PATH = '/Users/leehah/OnlineClass_Project/files/subcategories copy 8.json'

# Udemy API Info
API_CLIENT_ID = '4jOdAhTin8SeeTtpZlzxnkCiVcQiqfBbIktzZO8R'
API_CLIENT_SECRET = 'pr7dF6L70czRTO0k1MbtCeeE4rWFrrr249wY806cfmUE73SZn5DD2gmuHB5gxhKqIcBhdDxbGMEdh1ByIK7lZpiAyl4aG18uDBY8amQ76K0yqztHvYWv5JVh1jORJQfi'
BASE64_ID = 'NGpPZEFoVGluOFNlZVR0cFpsenhua0NpVmNRaXFmQmJJa3R6Wk84UjpwcjdkRjZMNzBjelJUTzBrMU1idENlZUU0cldGcnJyMjQ5d1k4MDZjZm1VRTczU1puNUREMmdtdUhCNWd4aEtxSWNCaGREeGJHTUVkaDFCeUlLN2xacGlBeWw0YUcxOHVEQlk4YW1RNzZLMHlxenRIdllXdjVKVmgxak9SSlFmaQ=='

# Udemy API URL
BASE_URL = 'https://www.udemy.com/api-2.0/'

# MySQL
DATABASE_TYPE = 'mysql'
DBAPI = 'mysqlconnector'
ENDPOINT = 'localhost'
USER = 'leehah'
PASSWORD = 'leehah'
PORT = 3306
DATABASE = 'OnlineClass'


def get_courses(page = 1, page_size = 100, subcategory = ''):
    url = f"{BASE_URL}courses/"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Basic {BASE64_ID}'}

    params = {
        'page': page,
        'page_size': page_size,
        'subcategory' : subcategory}

    response = requests.get(url, headers = headers, params = params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def fetch_all_courses():
    all_courses = []
    
    with open(SUBCATEGORY_FILE_PATH, 'r') as f:
        subcategory_list = json.load(f)

    print('-' * 40)
    for subcategory in subcategory_list:
        print(f'{subcategory} Crawing Start')
        page = 1
        page_size = 100
        while True:
            response = get_courses(page = page, page_size = page_size, subcategory = subcategory)
            if response and 'results' in response:
                for tmp_course in response['results']:
                    tmp_course['sub_category'] = subcategory
                all_courses.extend(response['results'])
                if len(response['results']) < page_size:
                    print(f'Finished subcategory: {subcategory}')
                    print('-' * 40)
                    break
                page += 1
            else:
                print(f'Failed subcategory: {subcategory}')
                print('-' * 40)
                break

    return all_courses

def main():
    all_courses = fetch_all_courses()
    print(f"Total courses fetched: {len(all_courses)}")
    raw_df = pd.DataFrame(all_courses)

    col_str_df = raw_df.astype({'id' : 'str',
                            'price_detail' : 'str',
                            'visible_instructors' : 'str',
                            'locale' : 'str',
                            'curriculum_lectures' : 'str',
                            'curriculum_items' : 'str'})

    try:
        db_connection_str = f'{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}'
        db_connection = create_engine(db_connection_str)
        conn = db_connection.connect()

        col_str_df.to_sql(name = 'udemy_class_list',
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