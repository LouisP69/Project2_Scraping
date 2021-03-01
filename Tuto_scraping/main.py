import requests
from bs4 import BeautifulSoup as bsp

# Create lists
product_url = []
UPC = []
title = []
prices_including_tax = []
prices_excluding_tax = []
number_available = []
product_description = []
category = []

# category = ['Travel', 'Mystery', 'Historical Fiction', 'Sequential Art', 'Classics', 'Philosophy', 'Romance',
#            'Womens Fiction', 'Fiction', 'Childrens', 'Religion', 'Nonfiction', 'Music', 'Default', 'Science Fiction',
#          'Sports and Games', 'Add a comment']
review_rating = []
image_url = []


# Define the number of pages
pages = [str(i) for i in range(1, 51)]

# First loop to parse and get all the pages
for page in pages:
    # Get the URL with requests to see if site is working
    response = requests.get('http://books.toscrape.com/catalogue/page-' + page + '.html')
    # Beautifulsoup to parse
    page_html = bsp(response.text, 'html.parser')
    # print(response)
    # attributes that we are looking for
    book_containers = page_html.find_all(attrs={'class': 'product_pod'})

    # Second loop to seek urls of each book in the website
    for book in book_containers:
        # Url
        a = book.find('a')
        url = a['href']
        product_url.append('https://books.toscrape.com/catalogue/' + url)

# Create csv file with all urls
with open('urls.csv', 'w') as file:
    for url in product_url:
        file.write(url + '\n')

# Third loop to get all information we need about each books
with open('urls.csv', 'r') as inf:
    with open('projet2.csv', 'w', newline='') as outf:
        outf.write('product_url, UPC, title, prices_excluding_tax, prices_including_tax, number_available, '
                   'product_description, category, review_rating, image_url\n')
        for row in inf:
            book_url = row.strip()
            response = requests.get(book_url)
            if response.ok:
                soup = bsp(response.text, 'html.parser')
                # UPC
                UPC = soup.find('table', {'class': 'table table-striped'}).find('td').text[0:]  # Slicing
                print(UPC)
                # Titre
                title = soup.find('h1').text[0:]
                print(title)
                # Price without taxes
                prices_excluding_tax = soup.find()
                # print(prices_excluding_tax)
                # Price with taxes
                prices_including_tax = soup.find()
                # print(prices_including_tax)
                # Number of products available
                number_available = soup.find('div', {'class': 'col-sm-6 product_main'}).find('p', {'class': 'instock availability'}).getText()
                print(number_available)
                # Description
                product_description = soup.find('article', {'class': 'product_page'}).find('div', {'id': 'product_description'}).find('p')
                print(product_description)
                # Categories
                category = soup.find('ul', {'class': 'nav nav-list'}).find('li')
                print(category)
                # print(category)
                # Notes
                review_rating = soup.find('p', {'class': 'star-rating'}).get('class')[1]  # To only get the number of stars
                print(review_rating)
                # Url image
                # image_url = soup.find("img").get("src"))
                # print(image_url)
