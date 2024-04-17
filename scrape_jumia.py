"""
Things I have to do are:
- Get the product i want to scrape from input
- create a function that will get all the links of the products listed on the page
- create a function that will handle pagination
- create a function that will get the details of the product
  create function that will add the data to a CSV file
"""

import requests
from bs4 import BeautifulSoup
import random
from urllib.parse import urljoin
from typing import Dict
import pandas as pd

user_agents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
]

user_agent = random.choice(user_agents)

custom_headers = {
    'user-agent': user_agent,
    'accept-language': 'en-GB,en;q=0.9',
}

link_group = set()
data = []
flag = True

def pagination(soup: BeautifulSoup) -> str:
    """handle paginations"""
    links= soup.select('a.pg')
    next_page = filter(lambda x: x.attrs.get('aria-label') == 'Next Page', links)
    if next_page:
        next_url = next_page.attrs.get('href')
        return(urljoin(url, next_url))
    flag = False
    return


def get_listing_urls(url: str) -> None:
    """get products listing urls"""
    response = requests.get(url, headers=custom_headers)
    soup = BeautifulSoup(response.text, 'lxml')
    product_links = soup.select('article.prd a.core')
    product_links = [urljoin(url, product_url.attrs.get('href')) for product_url in product_links]
    for link in product_links:
        if link not in link_group:
            link_group.add(link)


def get_product_details(product_url: str) -> Dict:
    """get the details of a product from its link"""
    response = requests.get(product_url, headers=custom_headers)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.select_one('div.-pls.h1.-pts').text.strip()
    price1 = soup.select_one('span.-b.-ubpt.-tal.-fs24.-prxs')
    price2 = soup.select_one('span.-tal.-gy5.-lthr.-fs16.-pvxs -ubpt')
    if price1:
        price = price1.text.strip()
    else:
        price = price2.text.strip()
    rating = soup.select_one('a.-plxs._more').text.strip()
    image = soup.select_one('a.itm img').attrs.get('src')
    description_list = soup.select('div.markup.-pam ul li')
    description = '\n'.join([desc.text.strip() for desc in description_list]).strip()
    return {
        "store": "Jumia",
        "title": title,
        "price": price,
        "rating": rating,
        "image": image,
        "description": description,
        "link": product_url
    }

def main():
    """driver"""
    search = input("What do you want recommendations for? ")
    if search != "":
        search = search.replace(" ", "-")
    else:
        exit(1)
    url = f'https://www.jumia.com/catalog/?q={search}'
    print(url)
    # while flag == True:
    get_listing_urls(url)
        # url = pagination(BeautifulSoup(requests.get(url, headers=custom_headers).text, 'lxml'))
    for link in link_group:
        data.append(get_product_details(link))
    df = pd.DataFrame(data)
    df.to_csv(f'{search}.csv', index=False)


if __name__ == '__main__':
    main()