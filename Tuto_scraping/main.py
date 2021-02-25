import requests
from bs4 import BeautifulSoup
import csv

# Create CSV file lists
product_url = []
UPC = []
title = []
prices_including_tax = []
prices_excluding_tax = []
number_available = []
product_description = []
category = []
review_rating = []
image_url = []

# Define the number of pages
pages = [str(i) for i in range(1, 51)]

# First loop to parse and get all the pages
for page in pages:
    # Get the URL with requests to see if site is working
    response = requests.get('http://books.toscrape.com/catalogue/page-' + page + '.html')
    # Beautifulsoup to parse
    page_html = BeautifulSoup(response.text, 'html.parser')
    # attributes that we are looking for
    book_containers = page_html.find_all(attrs={'class': 'product_pod'})
    print(response)

# Second loop to seek everything that we need
    for book in book_containers:
        # Url
        product_url.append(book.h3.a.get('href'))
        # Titre
        title.append(book.h3.a.get('title'))
        # Prix avec taxes
        prices_including_tax.append(book.find('p', class_="price_color").text[2:])  # Slicing price sign
        # Prix sans taxes
        prices_excluding_tax
        # Nombre de produits disponibles
        number_available.append(book.find('p', class_="instock availability"))
        # Description
        product_description
        # Catégories
        category
        # Notes
        review_rating.append(book.find("p", class_="star-rating").get("class")[1])  # To only get the number of stars
        # Url image
        image_url.append(book.find("img").get("src"))
        print(product_url)

# CSV file creation
with open('projet2.csv', 'w', newline='') as f:
    tableau = []
    ecrire = csv.writer(f)
    for i in tableau:
        ecrire.writerow(i)
