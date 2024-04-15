import requests
from bs4 import BeautifulSoup


url = 'https://www.amazon.com/s?k=bluetooth+earbuds&crid=2MS9IBH0IVQ7K&sprefix=bluetooth%2Caps%2C326&ref=nb_sb_ss_ts-doa-p_3_9'

custom_headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'accept-language': 'en-GB,en;q=0.9',
}

response = requests.get(url, headers=custom_headers)

soup = BeautifulSoup(response.text, 'lxml')
title_element = soup.select_one('.a-row')
print(soup.prettify())
