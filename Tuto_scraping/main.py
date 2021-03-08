import requests
from bs4 import BeautifulSoup as bsp
import csv

url_base = 'http://books.toscrape.com/'
# Create folder for all the csv files
csv_path = 'Scraped/'

# First function to seek books urls
def look_for_books_url(category_url: str):
    category = []
    links = []
    response = requests.get(category_url)
    if response.ok:
        category.append(category_url)
        category_base = category_url.replace('index.html', '')
        soup = bsp(response.content, 'html.parser')
        # Look for 'next' class to define if there is multiple pages
        while True:
            # if not we get out of the loop
            if not soup.find('li', class_='next'):
                break
            response = requests.get(category_base + soup.find('li', class_='next').a['href'])
            if response.ok:
                category.append(response.url)
                soup = bsp(response.content, 'html.parser')
    # Now we look for the books
    for book_url in category:
        response = requests.get(book_url)
        if response.ok:
            soup = bsp(response.content, 'html.parser')
            book_containers = soup.find_all(class_='product_pod')
            for book in book_containers:
                link = book.a['href']
                links.append(url_base + 'catalogue/' + link.replace('../../../', ''))
    return links


# Function to get all categories urls
def look_for_categories_url(url: str):
    cat = dict()
    response = requests.get(url)
    if response.ok:
        soup = bsp(response.content, 'html.parser')
        category_container = soup.find('ul', class_='nav-list').find('ul').find_all('a')
        for category in category_container:
            cat[category.text.strip().replace(' ', '_')] = category['href']
    return cat


# Function to go through each categories
def scrap_books_in_cat(url: str):
    all_cat = dict()
    categorys = look_for_categories_url(url)
    for category in categorys:
        # Loop to go through each books in each categories
        all_cat[category[0]] = look_for_books_url(url + category[1])
    return all_cat


def csv_writer(data: list, category: str):
    with open(csv_path + category + '.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['productpage_url', 'upc', 'title', 'price_including_tax',  'price_excluding_tax',
                      'number_available', 'product_description', 'category', 'review_rating', 'image_url']
        try:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='', extrasaction='raise')
            writer.writeheader()
            writer.writerows(data)
        except Warning:
            print('Erreur')

def final_script():
    urls = scrap_books_in_cat(url_base)
    for category in urls:
        data = []
        for books in urls:
            data.append(look_for_books_data(books))
        try:
            csv_writer(data, category)
        except Warning:
            print('Erreur')

# def look_for_books_data(url: str):
#     info = []
#     response = requests.get(url)
#     if response.ok:
#         soup = bsp(response.content, 'html.parser')
#         img = url_base + soup.select("div.item.active")[0].img.attrs["src"].replace("../../", "")
#         # Almost all datas are stored in one place
#         data_container = soup.find_all('table')[0].find_all('td')
#         for data in data_container:
#             info.append(data.text)
#         return(
#             'product_page_url' = url,
#             # UPC
#             'upc' = info[0],
#             # Title
#             'title' = soup.find_all("div", class_="product_main")[0].h1.text,
#             # Price including tax
#             'price_including_tax' = info[3],
#             # Price excluding tax
#             'price_excluding_tax' = info[2],
#             # Number available
#             'number_available' = info[5].text[10:12], # Slicing to only get the number available
#             # Description
#             'product_description' = soup.find('article', {'class': 'product_page'}).find_all('p')[3].get_text(),
#             # Categories
#             'categories' = soup.find('ul', class_='breadcrumb').find_all('a')[2].text,
#             # Number of stars
#             'review_rating' = soup.find_all('p', class_='star-rating')[0].attrs['class'][1], # Slicing to get only the number of stars
#             # Images
#             'image_url' = img
#         )