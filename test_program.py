import sqlite3
import pandas as pd

conn = sqlite3.connect('tiki.db')
# cur = conn.cursor() # do not need this. can run without pandas

db = pd.read_sql_query(
    '''SELECT * 
    FROM categories 
    ORDER BY cat_id;
    ''', conn)

db.to_csv('tiki_categories.csv', index = False) # index to false, because we already have an ID

db = pd.read_sql_query(
    '''SELECT * 
    FROM product_table 
    ORDER BY p_id;
    ''', conn)

db.to_csv('tiki_products.csv', index = False) # index to false, because we already have an ID