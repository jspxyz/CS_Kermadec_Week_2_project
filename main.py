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

# Functions to run entire program
# get_url(TIKI_URL)               # function to get Tiki url
# create_categories_table()       # creating category table
    # commented out here but left a command line to run function
    # underneath the function code

from bs4 import BeautifulSoup
import requests
import sqlite3

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