# Kermadec Week 2 project crawl Tiki categories & products

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
