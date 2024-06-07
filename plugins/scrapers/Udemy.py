import requests

# Udemy API Info
API_CLIENT_ID = '4jOdAhTin8SeeTtpZlzxnkCiVcQiqfBbIktzZO8R'
API_CLIENT_SECRET = 'pr7dF6L70czRTO0k1MbtCeeE4rWFrrr249wY806cfmUE73SZn5DD2gmuHB5gxhKqIcBhdDxbGMEdh1ByIK7lZpiAyl4aG18uDBY8amQ76K0yqztHvYWv5JVh1jORJQfi'
BASE64_ID = 'NGpPZEFoVGluOFNlZVR0cFpsenhua0NpVmNRaXFmQmJJa3R6Wk84UjpwcjdkRjZMNzBjelJUTzBrMU1idENlZUU0cldGcnJyMjQ5d1k4MDZjZm1VRTczU1puNUREMmdtdUhCNWd4aEtxSWNCaGREeGJHTUVkaDFCeUlLN2xacGlBeWw0YUcxOHVEQlk4YW1RNzZLMHlxenRIdllXdjVKVmgxak9SSlFmaQ=='

# Udemy API URL
BASE_URL = 'https://www.udemy.com/api-2.0/'

def get_courses(page = 1, page_size = 100, category = ''):
    url = f"{BASE_URL}courses/"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Basic {BASE64_ID}'}

    params = {
        'page': page,
        'page_size': page_size,
        'subcategory' : category}

    response = requests.get(url, headers = headers, params = params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def fetch_all_courses():
    all_courses = []
    page = 1
    page_size = 100
    category = 'Esoteric Practices'

    while True:
        response = get_courses(page = page, page_size = page_size, category = category)
        if response and 'results' in response:
            all_courses.extend(response['results'])
            if len(response['results']) < page_size:
                break
            page += 1
            print(page)
        else:
            print('finish')
            break

    return all_courses

def main():
    all_courses = fetch_all_courses()
    print(len(all_courses))
    # for course in all_courses:
    #     print(f"Title: {course['title']}")
    #     print(f"URL: {course['url']}")
    #     print(f"Price: {course['price']}")
    #     print("-" * 40)

if __name__ == '__main__':
    main()
