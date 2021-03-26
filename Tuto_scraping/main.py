import requests
from bs4 import BeautifulSoup as bsp
import csv
import os
from multiprocessing import Pool


url_base = 'http://books.toscrape.com/'
csv_path = "scraped/"
image_path = "scraped/images/"


def init():
    path = os.path.dirname(os.path.realpath(__file__))
    try:
        os.makedirs(path + "//" + image_path, exist_ok=True)
    except OSError as error:
        print("Error : the file cannot be created :" + str(error))


def look_for_books_data(url: str):
    """ Function to scrape books data"""
    info = []
    response = requests.get(url)
    if not response.ok:
        print("L'url : " + url + 'est momentanément indisponible.')
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


def look_for_books_url(category_url: str) -> list:
    """ Function to seek books urls"""
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
            if not response.ok:
                print('Le site ' + url_base + ' est momentanément indisponible.')
            if response.ok:
                category.append(response.url)
                soup = bsp(response.content, 'html.parser')


    # Now we look for the books
    for book_url in category:
        response = requests.get(book_url)
        if not response.ok:
            print("L'url : " + book_url + 'est momentanément indisponible.')
        if response.ok:
            soup = bsp(response.content, 'html.parser')
            book_containers = soup.find_all(class_='product_pod')

            for book in book_containers:
                link = book.a['href']
                links.append(
                    url_base + 'catalogue/' + link.replace('../../../', ''))  # To concatenate we have to replace

    return links


def look_for_categories_url(url: str):
    """ Function to get all categories urls"""
    categorys = dict()
    response = requests.get(url)
    if not response.ok:
        print("L'url : " + url + 'est momentanément indisponible.')
    if response.ok:
        soup = bsp(response.content, 'html.parser')
        category_container = soup.find('ul', class_='nav-list').find('ul').find_all('a')

        for category in category_container:
            categorys[category.text.strip().replace(' ', '_')] = category['href']

    return categorys


def scrap_books_in_cat(url: str):
    """ Function to go through each categories"""
    all_category = dict()
    categorys = look_for_categories_url(url)

    for category in categorys.items():
        # Loop to go through each books in each categories
        all_category[category[0]] = look_for_books_url(url + category[1])
        print(f'Récupération des livres dans la catégorie : {category[0]}')

    return all_category


def csv_writer(data: list, category: str):  # First we say that there will be two different parameter and what they are
    """ We create the CSV file"""
    with open(csv_path + category + '.csv', 'w', newline='',
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
            print("Erreur dans l'extraction des informations : " + str(error))
            raise Warning


def scrap_book_picture(img_url: str):
    response = requests.get(img_url)
    if response.ok:
        with open(image_path + img_url.split('/')[-1], 'wb') as pics:
            pics.write(response.content)
    else:
        print("Error in the download of the images :" + img_url)


def main():
    """ Function to run our program"""
    init()
    print('Début du scraping sur le site ' + url_base)
    urls = scrap_books_in_cat(url_base)
    img_all = []
    # First loop : we look for all the categories urls
    for category in urls.keys():
        data = []
        # Second loop : we look for each book in each categories
        for books in urls[category]:
            print(f"Récupération des informations sur l'url {books!r} dans la catégorie {category!r}")
            data.append(look_for_books_data(books))
            img_all.append(data[-1]['image_url'])
        try:
            csv_writer(data, category)
            print(f"Tous les livres de la catégorie {category!r} ont été récupérés")

        except Warning:
            print("Une erreur s'est produite lors de la création du fichier csv")

    print("Récupération des images..")
    map(scrap_book_picture, img_all)
    print("Images récupérées !")


if __name__ == '__main__':
    main()
