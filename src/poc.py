import os
from dotenv import load_dotenv
load_dotenv()

import requests
import pandas as pd

url = f"https://newsdata.io/api/1/latest?apikey={os.getenv('API_KEY')}"
response = requests.get(url)
data = response.json()


df = pd.DataFrame.from_dict(data['results'], orient='columns')
print(df.head(10))
df.to_csv('data/poc.csv')