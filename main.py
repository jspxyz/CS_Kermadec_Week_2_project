# Kermadec Week 2 project crawl Tiki categories & products

''' Steps to crawl products
Step 1 - create table with all possible categories in TIKI. Use create_categories_table
Step 2 - create product table . use create_categories_table template and replace the variables
  - include the category ID
  - must match IDs to be able to join (using primary key)
Step 3 - for each cateogry in this table, pull the URL, and repeat the steps from Week 1
 - can replace the URL from Week 1 project from the URL from the table
 - use a for loop to repeat process
 - get to the last category layer first to scrap, to avoid repeating products
 - lowest level cat doesn't have a sub category. use to check.
    - either create a child ID OR
    - use LEFT JOIN to get all sub category
        - if sub category is equal to NULL, then this is the website to crawl
Step 4 - get_all_categories(main_categories,save_db = TRUE) is the final step to save
'''

# Functions and classes for entire program
# function to get_url(url)
# function to create category table 
# creating class Category
# function to get main categories
# function to get sub categories
# function to get all categories
# section to clean tables and start over, if needed

from bs4 import BeautifulSoup
import requests
import sqlite3
import re
import pandas as pd
import time
import random

TIKI_URL = 'https://tiki.vn'

#step - create empty database
conn = sqlite3.connect('tiki.db')
cur = conn.cursor()

# Function
# Get the HTML content get_url()
def get_url(url):
    try:
        response = requests.get(url).text
        soup = BeautifulSoup(response, 'html.parser')
        return soup
    except Exception as err:
        print('ERROR BY REQUEST:', err)

# Function
# Create table categories in the database using a function
# cat_id = primary key id
# name = category title
# url = category page
# parent_id = parent id number
# sub_category_count = number of sub categories under each category
    # using this to add a column to know if a category is at the lowest level
# create_at = timestamp of when this was created
def create_categories_table():
    query = """
        CREATE TABLE IF NOT EXISTS categories (
            cat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            url TEXT, 
            parent_id INTEGER, 
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    try:
        cur.execute(query)
        conn.commit()
    except Exception as err:
        print('ERROR BY CREATE CATEGORIES TABLE', err)

# Function
# Create productd table in the database using a function
def create_product_table():
    query = """
        CREATE TABLE IF NOT EXISTS product_table (
            p_id INTEGER PRIMARY KEY AUTOINCREMENT,
            p_title VARCHAR(255),
            cat_id INTEGER,
            seller_product_id INTEGER,
            sku INTEGER,
            price INTEGER,
            p_product_id INTEGER,
            brand TEXT,
            category TEXT, 
            p_url TEXT,
            img_url TEXT,
            p_original_price INTEGER,
            discount VARCHAR(255),
            refund VARCHAR(255),
            TIKI_now VARCHAR(255),
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    try:
        cur.execute(query)
        conn.commit()
    except Exception as err:
        print('ERROR BY CREATE PRODUCT TABLE', err)
        

# Instead of using a function to do CRUD on database,
# creating a class Category is preferred
# attributes: name, url, parent_id
# instance method: save_into_db()
class Category:
    def __init__(self, name, url, parent_id=0, cat_id=None): 
        self.cat_id = cat_id # these are the same categories as in SQL database made above
        self.name = name
        self.url = url
        self.parent_id = parent_id

    def __repr__(self):
        return f"ID: {self.cat_id}, Name: {self.name}, URL: {self.url}, Parent: {self.parent_id}"

    def save_into_db(self): # saving itself into a table. same as INSERT ROW OF DATA section above
        query = """
            INSERT INTO categories (name, url, parent_id)
            VALUES (?, ?, ?);
        """
        val = (self.name, self.url, self.parent_id)
        try:
            cur.execute(query, val)
            self.cat_id = cur.lastrowid
            conn.commit()
        except Exception as err:
            print('ERROR BY CATEGORY TABLE INSERT:', err)


# creating a class Product
class Product:
    def __init__(self, p_title, cat_id, seller_product_id, sku, price, p_product_id, brand, category, p_url, img_url, p_original_price, discount, refund, TIKI_now, p_id=None,): 
        self.p_id = p_id # these are the same categories as in SQL database made above
        self.p_title = p_title
        self.cat_id = cat_id
        self.seller_product_id = seller_product_id
        self.sku = sku
        self.price = price
        self.p_product_id = p_product_id
        self.brand = brand
        self.category = category
        self.p_url = p_url
        self.img_url = img_url
        self.p_original_price = p_original_price
        self.discount = discount
        self.refund = refund
        self.TIKI_now = TIKI_now

    def __repr__(self):
        return f"P_ID: {self.p_id}, Title: {self.p_title}, Cat_ID: {self.cat_id}, Seller_Product_ID: {self.seller_product_id}, SKU: {self.sku}, Price: {self.price}, P_Product_ID: {self.p_product_id}, Brand: {self.brand}, Category: {self.category}, P_URL: {self.p_url}, IMG_URL: {self.img_url}, P_Original_Price: {self.p_original_price}, Discount: {self.discount}, Refund: {self.refund}, TIKI_now: {self.TIKI_now}"

    def save_into_db(self): # saving itself into a table. same as INSERT ROW OF DATA section above
        column_list = ['p_title', 
                       'cat_id', 
                       'seller_product_id', 
                       'sku', 
                       'price', 
                       'p_product_id', 
                       'brand', 
                       'category',
                       'p_url', 
                       'img_url', 
                       'p_original_price',
                       'discount',
                       'refund',
                       'TIKI_now']
        query = f"""
            INSERT INTO product_table ({', '.join(column_list)})
            VALUES ({', '.join(['?' for _ in range(len(column_list))])});
        """
        val = (self.p_title, self.cat_id, self.seller_product_id, self.sku, self.price, self.p_product_id, self.brand, self.category, self.p_url, self.img_url, self.p_original_price, self.discount, self.refund, self.TIKI_now)
        try:
            cur.execute(query, val)
            self.p_id = cur.lastrowid
            conn.commit()
        except Exception as err:
            print('ERROR BY PRODUCT TABLE INSERT:', err)

# Function
# getting main categories function
def get_main_categories(save_db=False): # default to False because you don't want to store faulty data
    soup = get_url(TIKI_URL)

    result = []
    for a in soup.find_all('a', {'class': 'MenuItem__MenuLink-sc-181aa19-1 fKvTQu'}):
        name = a.find('span', {'class': 'text'}).text
        url = a['href']
        main_cat = Category(name, url) # creating object from class Category

        if save_db: # only save to db if save_db is TRUE. defaulted to FALSE
            main_cat.save_into_db()
        result.append(main_cat)
    return result


# get_sub_categories() given a parent category
def get_sub_categories(parent_category, save_db=False):
    parent_url = parent_category.url
    result = []

    try:
        soup = get_url(parent_url)
        div_containers = soup.find_all('div', {'class':'list-group-item is-child'}) # getting sub categories
        # input sub_category_count
        for div in div_containers:
            name = div.a.text

            # replace spaces that appear > 2 times with one space
            # replace new line with space as well
            name = re.sub('(\s{2,}|\n+)', ' ', name)

            sub_url = TIKI_URL + div.a['href']
            cat = Category(name, sub_url, parent_category.cat_id) # we now have parent_id, which is cat_id of parent category
            if save_db:
                cat.save_into_db()
            result.append(cat)
    except Exception as err:
        print('ERROR BY GET SUB CATEGORIES:', err)
    return result

# get_all_categories() given a list of main categories (This is a recursion function)
def get_all_categories(categories,save_db=False):
    # if i reach the last possible category, this function will stop because
    # the length of the last category will be an empty list
    if len(categories) == 0: # this is the stop condition
        return
    for cat in categories:
        sub_categories = get_sub_categories(cat, save_db=save_db)
        print(f'{cat.name} has {len(sub_categories)} sub-categories')
        get_all_categories(sub_categories, save_db=True)


# creating function to scrape products
def get_products_one_page(url, cat_id, save_db=False):
    prod_result = []
  
    try:
        soup = get_url(url)

        product_list = soup.find('div',{'class':'product-box-list'})

        # get list of all div class 'product-item'
        product_items_div = product_list.find_all('div',{'class':'product-item'})
        
        # remove div_containers = soup.find_all('div', {'class':'list-group-item is-child'}) # getting sub categories
        for i in range(len(product_items_div)):
            # p_id leaving out since this is the pirmary key
            p_title = product_items_div[i]['data-title']
            seller_product_id = product_items_div[i]['data-seller-product-id'] 
            sku = product_items_div[i]['product-sku']
            price = product_items_div[i]['data-price']
            p_product_id = product_items_div[i]['data-id']
            brand = product_items_div[i]['data-brand'] 
            category = product_items_div[i]['data-category']
            # pulling information from level below div with different tags
            p_url = product_items_div[i].a['href']
            img_url = product_items_div[i].img['src']
            try:
              p_original_price = product_items_div[i].find('span',{'class':'price-regular'}).text
              p_original_price = ''.join(p_original_price.split('.')).strip('đ')
              discount = product_items_div[i].find('span',{'class':'sale-tag sale-tag-square'}).text
            except:
              p_original_price = price
              discount = '0%'
            # adding discount if available
            try:
              if product_items_div[i].find('div',{'class':'badge-under_price'}).img['src']:
                refund = 'Yes'
            except:
              refund = 'No'
            
            # additng Tiki_now if available
            try:                    
              if product_items_div[i].find('div',{'class':'item'}).img['src']:
                TIKI_now = 'Yes'
            except:
              TIKI_now = 'No'
            prod = Product(
                p_title=p_title,
                cat_id=cat_id,
                seller_product_id=seller_product_id,
                sku=sku,
                price=price,
                p_product_id=p_product_id,
                brand=brand,
                category=category,
                p_url=p_url,
                img_url=img_url,
                p_original_price=p_original_price,
                discount=discount,
                refund=refund,
                TIKI_now=TIKI_now) 

            if save_db:
                prod.save_into_db()
            prod_result.append(prod)
    except Exception as err:
        print('ERROR BY GET_PRODUCTS_ONE_PAGE:', err)
    return prod_result

## while function to repeat category scrape
finalData = []
def get_one_category_scrape(url, cat_id):
    product_items_div_length_Loop = 1
    i = 1

    while product_items_div_length_Loop != 0:
        path = url + '&page=' + str(i)
        print(path) # to print path while loop is running to make sure that something is happening
        result = get_products_one_page(path, cat_id, save_db=True)
        product_items_div_length_Loop = len(result)
        print(product_items_div_length_Loop) # another check to see the output of each page
        finalData.extend(result)
        i+=1
        time.sleep(random.randint(2,4))
    
    return finalData


# drop the whole table to clean things up
# this actually drops all data from database to start over
# this helps for testing
# commented out entire section

# clearing the database
# cur.execute('DROP TABLE categories;')
cur.execute('DROP TABLE product_table;')
conn.commit()

# creating tables
# create_categories_table()
create_product_table()


# RUNNING ALL FUNCTIONS

# running get_main_categories
# saving to database
# assigning as main_categories
# main_categories = get_main_categories(save_db = True)

# code to run and collect all categories
# get_all_categories(main_categories,save_db=True)

# create table of lowest level categories
sub_cat_crawl_db = pd.read_sql_query(
    '''SELECT *
    FROM categories
    WHERE cat_id NOT IN (SELECT parent_id FROM categories) AND parent_id != 0
    ORDER BY cat_id''', conn)

# create list of just cat_id and url
sub_cat_crawl_list = sub_cat_crawl_db[['cat_id','url']]


# for loop to run scraping functions (one page & categories)
for cat_id, url in sub_cat_crawl_list.values:
  print(url, cat_id)
  get_one_category_scrape(url, cat_id)

