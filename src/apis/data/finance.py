import os
import requests
from dotenv import load_dotenv

load_dotenv()

ALPHA_KEY = os.getenv('ALPHA_KEY')
ALPHA_API= os.getenv('ALPHA_API')

def get_stock_data(symbol):
    url = f'{ALPHA_API}&symbol={symbol}&apikey={ALPHA_KEY}'
    response = requests.get(url)
    data = response.json()
    return data
