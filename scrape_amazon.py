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
import time

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

def pagination(soup: BeautifulSoup, url: str) -> str:
    """handle paginations"""
    next_page = soup.select_one('a.s-pagination-next')
    if next_page:
        next_url = next_page.attrs.get('href')
        return(urljoin(url, next_url))
    flag = False
    return None


def get_listing_urls(url: str) -> None:
    """get products listing urls"""
    response = requests.get(url, headers=custom_headers)
    soup = BeautifulSoup(response.text, 'lxml')
    product_links = soup.select('[data-asin] h2 a')
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
    title = soup.select_one('span#productTitle').text.strip()
    price = soup.select_one('span.a-offscreen').text.strip()
    rating = soup.select_one('span.a-size-base.a-color-base').text.strip()
    image = soup.select_one('img#landingImage').attrs.get('src')
    description_list = soup.select('div#feature-bullets ul.a-spacing-mini li span.a-list-item')
    description = '\n'.join([desc.text.strip() for desc in description_list]).strip()
    return {
        "store": "Amazon",
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
    search_url = f'https://www.amazon.com/s?k={search}'
    
    start = time.time()
    get_listing_urls(search_url)
    url = search_url
    page = 1
    while flag == True and page < 4:
        url = pagination(BeautifulSoup(requests.get(url, headers=custom_headers).text, 'lxml'), search_url)
        if url:
            get_listing_urls(url)
        else:
            break
        page += 1

    print("getting product details")
    for link in link_group:
        data.append(get_product_details(link))
    df = pd.DataFrame(data)
    df.to_csv(f'{search}.csv', index=False)
    print(f"Time taken: {time.time() - start}")


if __name__ == '__main__':
    main()