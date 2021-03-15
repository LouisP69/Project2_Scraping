import requests
from bs4 import BeautifulSoup as bsp
import csv

url_base = 'http://books.toscrape.com/'


"""Function to scrape books data"""


def look_for_books_data(url: str):
    info = []
    response = requests.get(url)
    if response.ok:
        soup = bsp(response.content, 'html.parser')
        img = url_base + soup.select("div.item.active")[0].img.attrs["src"].replace("../../", "")
        # Almost all datas are stored in one place
        data_container = soup.find_all('table')[0].find_all('td')

        for data in data_container:
            info.append(data.text)

        return {
            'product_page_url': url,
            # UPC
            'upc': info[0],
            # Title
            'title': soup.find_all("div", class_="product_main")[0].h1.text,
            # Price including tax
            'price_including_tax': info[3],
            # Price excluding tax
            'price_excluding_tax': info[2],
            # Number available
            'number_available': info[5],  # Slicing to only get the number available
            # Description
            'product_description': soup.find('article', {'class': 'product_page'}).find_all('p')[3].get_text(),
            # Categories
            'category': soup.find('ul', class_='breadcrumb').find_all('a')[2].text,
            # Number of stars
            'review_rating': soup.find_all('p', class_='star-rating')[0].attrs['class'][1],
            # Slicing to get only the number of stars
            # Images
            'image_url': img
        }

    else:
        print("L'url : " + url + 'est momentanément indisponible.')


""" Function to seek books urls"""


def look_for_books_url(category_url: str) -> list:
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

    else:
        print('Le site ' + url_base + ' est momentanément indisponible.')

    # Now we look for the books
    for book_url in category:
        response = requests.get(book_url)
        if response.ok:
            soup = bsp(response.content, 'html.parser')
            book_containers = soup.find_all(class_='product_pod')

            for book in book_containers:
                link = book.a['href']
                links.append(
                    url_base + 'catalogue/' + link.replace('../../../', ''))  # To concatenate we have to replace

        else:
            print("L'url : " + book_url + 'est momentanément indisponible.')

    return links


""" Function to get all categories urls"""


def look_for_categories_url(url: str):
    categorys = dict()
    response = requests.get(url)
    if response.ok:
        soup = bsp(response.content, 'html.parser')
        category_container = soup.find('ul', class_='nav-list').find('ul').find_all('a')

        for category in category_container:
            categorys[category.text.strip().replace(' ', '_')] = category['href']

    else:
        print("L'url : " + url + 'est momentanément indisponible.')

    return categorys


"""" Function to go through each categories"""


def scrap_books_in_cat(url: str):
    all_category = dict()
    categorys = look_for_categories_url(url)

    for category in categorys.items():
        """" Loop to go through each books in each categories"""
        all_category[category[0]] = look_for_books_url(url + category[1])
        print(f'Récupération des livres dans la catégorie : {category[0]}')

    return all_category


""" We create the CSV file"""


def csv_writer(data: list, category: str):  # First we say that there will be two different parameter and what they are
    with open(category + '.csv', 'w', newline='',
              encoding='utf-8-sig') as csvfile:  # We, then, name the files with the list "category"
        fieldnames = ['product_page_url', 'upc', 'title', 'price_including_tax', 'price_excluding_tax',
                      # Here we name all the columns in our CSV file
                      'number_available', 'product_description', 'category', 'review_rating', 'image_url']
        # Here we set what our CSV file will do in case of an error
        # Restval is for the values that are not in any fields
        try:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='', extrasaction='raise')
            writer.writeheader()
            writer.writerows(data)
            # The extrasaction was set to raise to put this "ValueError" line in case of an error
        except ValueError as error:
            print('Erreur ' + str(error))
            raise Warning


"""Function to run our program"""


def main():
    print('Début du scraping sur le site ' + url_base)
    urls = scrap_books_in_cat(url_base)
    # First loop : we look for all the categories urls
    for category in urls.keys():
        data = []

        # Second loop : we look for each book in each categories
        for books in urls[category]:
            print(f'Récupération des informations du livre {books!r} dans la catégorie {category!r}')
            data.append(look_for_books_data(books))
        try:
            csv_writer(data, category)
            print(f'Tous les livres de la catégorie {category!r} ont été récupérés')
        except Warning:
            print('Erreur')


if __name__ == '__main__':
    main()
