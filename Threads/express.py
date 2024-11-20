from bs4 import BeautifulSoup
import requests
import sys
import io


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = "https://e.vnexpress.net/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    path = soup.find('section', id="wrapper_container")


    if path:
 
        div = path.find('div', class_="col-left-topstory flexbox")

        if div:
            print(div.prettify())

            for child in div.find_all():
                print(child.text.strip())
        else:
            print("ERROR")
    else:
        print("ERROR")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")