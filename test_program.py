import sqlite3
import pandas as pd

conn = sqlite3.connect('tiki.db')
# cur = conn.cursor() # do not need this. can run without pandas

db = pd.read_sql_query(
    '''SELECT * 
    FROM categories 
    ORDER BY id;
    ''', conn)

db.to_excel('tiki_db.xlsx', index = False) # index to false, because we already have an ID