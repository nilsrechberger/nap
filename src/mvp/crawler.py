import os
from dotenv import load_dotenv
load_dotenv()

import requests
import pandas as pd

def fetch_data(country: str) -> None:
    url = f"https://newsdata.io/api/1/latest?apikey={os.getenv('API_KEY')}&country={country}"
    response = requests.get(url)
    return response.json()

if __name__ == '__main__':
    assert fetch_data().status_code == 200
    print("All good - Got 200 Response")