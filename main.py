from email.contentmanager import raw_data_manager
import pandas as pd

from src.mvp.crawler import fetch_data
from src.mvp.processor import *

if __name__ == '__main__':

    results = pd.DataFrame()

    countries = [
        'ch',
        'de',
        'at'
    ]
    
    for country in countries:
        raw_data = fetch_data(country)
        table = as_table(raw_data)
        results = pd.concat([results, table], ignore_index=True)

    clean_results = remove_paid_content(results)
    print(clean_results)

    clean_results.to_csv('data/mvp/mvp.csv')