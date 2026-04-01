# Data handling
import pandas as pd

# Project packages
from src.crawler import fetch_data
from src.processor import *

def main():
    results = pd.DataFrame()

    eu_countries = [
        "at", "be", "bg", "cy", "cz", "de", "dk", "ee", "es", "fi", 
        "fr", "gr", "hr", "hu", "ie", "it", "lt", "lu", "lv", "mt", 
        "nl", "pl", "pt", "ro", "se", "si", "sk"
    ]
    
    for country in eu_countries:
        raw_data = fetch_data(country)
        table = as_table(raw_data)
        results = pd.concat([results, table], ignore_index=True)
    
    results.to_csv('data/raw/raw_data.csv')

    clean_results = remove_paid_content(results)
    print(clean_results)

    clean_results.to_csv('data/processed/precessed_data.csv')

if __name__ == '__main__':
    main()