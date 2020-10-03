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

from bs4 import BeautifulSoup
import requests
import sqlite3
import re
import pandas as pd

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
def create_categories_table():
    query = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        print('ERROR BY CREATE TABLE', err)
        
create_categories_table()

# Instead of using a function to do CRUD on database,
# creating a class Category is preferred
# attributes: name, url, parent_id
# instance method: save_into_db()
class Category:
    def __init__(self, name, url, parent_id=None, cat_id=None): 
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
            print('ERROR BY INSERT:', err)

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

# running get_main_categories and saving to database
# get_main_categories(save_db = True)

# get_sub_categories() given a parent category
def get_sub_categories(parent_category, save_db=False):
    parent_url = parent_category.url
    result = []

    try:
        soup = get_url(parent_url)
        div_containers = soup.find_all('div', {'class':'list-group-item is-child'}) # getting sub categories
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
        get_all_categories(sub_categories)