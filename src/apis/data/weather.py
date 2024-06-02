import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_BASE_URL = os.getenv("WEATHER_BASE_URL")

def fetch_weather_data(location_id):
    """Fetches weather data from AccuWeather API (replace with your implementation)"""
    base_url = f"{WEATHER_BASE_URL}/forecasts/v1/hourly/12hour/"
    query_params = {
        "apikey": WEATHER_API_KEY,
        "metric": "true"
    }
    response = requests.get(f"{base_url}{location_id}", params=query_params)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch weather data: {response.status_code}")
        return None
    
def fetch_location_id(city_name):
    """Fetches location ID from AccuWeather API (replace with your implementation)"""
    base_url = f"{WEATHER_BASE_URL}/locations/v1/cities/search"
    query_params = {
        "apikey": WEATHER_API_KEY,
        "q": city_name
    }
    response = requests.get(base_url, params=query_params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['Key']
        else:
            logging.error(f"No location found for city: {city_name}")
            return None
    else:
        logging.error(f"Failed to fetch location ID: {response.status_code}")
        return None