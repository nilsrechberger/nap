from email.contentmanager import raw_data_manager
import pandas as pd

from src.mvp.crawler import fetch_data
from src.mvp.processor import *

if __name__ == '__main__':
    raw_data = fetch_data()
    table = as_table(raw_data)
    clean_table = remove_paid_content(table)

    clean_table.to_csv('data/mvp/mvp.csv')