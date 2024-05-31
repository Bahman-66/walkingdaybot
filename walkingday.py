import os
import logging
import requests
from dateutil import parser 
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, timedelta
from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

user_requests = defaultdict(lambda: {'count': 0, 'timestamp': datetime.now()})

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
PORT = int(os.getenv('PORT', 8443))
WEBHOOK = os.getenv('WEBHOOK')
MODEL = os.getenv('MODEL')

# Initialize application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Global dictionary to store user requests and location IDs
user_requests = {}
user_location_ids = {}
user_states = {}

def format_time(datetime_str):
    """Converts ISO 8601 date-time string to a more human-friendly time format."""
    dt = parser.parse(datetime_str)
    return dt.strftime("%-I %p") 

def create_menu_keyboard():
    """Creates a keyboard with buttons for menu options."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("Go for a Walk "), KeyboardButton("About Bot ")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def create_weather_prompt(weather_data):
    """Creates a prompt for analyzing weather data."""
    prompt = "Analyze the following weather data and determine the best time for a walk considering temperature and rain probability:\n\n"
    prompt += "Weather Forecast:\n"
    for hour in weather_data:
        time = format_time(hour['DateTime'])
        temperature = hour['Temperature']['Value']
        condition = hour['IconPhrase']
        precipitation_probability = hour['PrecipitationProbability']

        prompt += f"- Time: {time}\n"
        prompt += f"  - Temperature: {temperature}°C\n"
        prompt += f"  - Weather Condition: {condition}\n"
        prompt += f"  - Probability of Precipitation: {precipitation_probability}%\n\n"

    prompt += "Based on the weather forecast, it is recommended to avoid walking during periods of high temperature or heavy rain, and prefer cooler or less rainy periods.\n"
    prompt += "What is the best time for a walk?"

    return prompt

def fetch_weather_data(location_id):
    """Fetches weather data from AccuWeather API (replace with your implementation)"""
    base_url = "http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/"
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

def call_openai_api(prompt):
    """Interacts with OpenAI API (replace with your implementation)"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 250
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch response from OpenAI API: {response.status_code}")
        return None

def fetch_location_id(city_name):
    """Fetches location ID from AccuWeather API (replace with your implementation)"""
    base_url = "http://dataservice.accuweather.com/locations/v1/cities/search"
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

async def start(update: Update, context: CallbackContext):
    """Sends a welcome message with the menu keyboard."""
    intro_text = "Welcome to WalkingDay bot! I can help you with:\n"  # Customize your introduction
    await update.message.reply_text(intro_text, reply_markup=create_menu_keyboard())

async def walk(update: Update, context: CallbackContext):
    """Handles the /walk command (replace with your existing implementation)"""
    user = update.effective_user
    user_id = user.id

    logging.info(f"Walk: {user.mention_html()}")

    # Check if user data exists, if not, initialize it
    if user_id not in user_requests:
        user_requests[user_id] = {'count': 0, 'timestamp': datetime.now()}

    # Check request limits
    user_data = user_requests[user_id]
    current_time = datetime.now()

    # Reset count if 24 hours have passed since the first request
    if current_time - user_data['timestamp'] > timedelta(hours=24):
        user_data['count'] = 0
        user_data['timestamp'] = current_time

    if user_data['count'] >= 3:
        await update.message.reply_text("You have reached your request limit for today. Please try again tomorrow.")
        return

    # Ensure user has a location ID set
    if user_id not in user_location_ids:
        await update.message.reply_html(
            f"Dear {user.mention_html()}, please set your location first using /setlocation <city_name>.",
            reply_markup=ForceReply(selective=True),
        )
        return

    location_id = user_location_ids[user_id]
    weather_data = fetch_weather_data(location_id)

    if weather_data:
        # Prepare input for the model (replace with your existing logic)
        prompt = create_weather_prompt(weather_data)

        # Make request to GPT-4 API with the correct parameters (replace with your implementation)
        response = call_openai_api(prompt)

        if response:
            # Extract and print the response from the API (replace with your existing logic)
            await update.message.reply_html(
                response['choices'][0]['message']['content'].replace("user", user.mention_html()),
                reply_markup=ForceReply(selective=True),
            )
        else:
            await update.message.reply_text("Failed to fetch response from OpenAI API")
    else:
        await update.message.reply_html(
            f"Dear {user.mention_html()}, weather information is missing, please try later.",
            reply_markup=ForceReply(selective=True),
        )

async def handle_menu_button(update: Update, context: CallbackContext):
    """Handles user interaction with menu buttons."""
    user_choice = update.message.text.strip()
    user_id = update.effective_user.id

    if user_choice == "Go for a Walk":
        user_states[user_id] = 'awaiting_location'
        await update.message.reply_text("Please provide your location (city name):", reply_markup=ForceReply(selective=True))
    elif user_choice == "About Bot":
        about_bot_text = "This bot helps you with finding the best time for a walk based on the weather forecast. Feel free to explore the options!"
        await update.message.reply_text(about_bot_text)
    else:
        await update.message.reply_text("Invalid option. Please choose from the menu.")

async def handle_location_input(update: Update, context: CallbackContext):
    """Handles user input for location after selecting 'Go for a Walk'."""
    user_id = update.effective_user.id
    if user_states.get(user_id) == 'awaiting_location':
        city_name = update.message.text.strip()
        location_id = fetch_location_id(city_name)

        if location_id:
            user_location_ids[user_id] = location_id
            user_states[user_id] = None  # Reset user state
            await update.message.reply_text(f"Location set to {city_name}. Now processing your walk request...")
            await walk(update, context)  # Call the walk function
        else:
            await update.message.reply_text("Could not find location. Please try again with a valid city name.")
    else:
        await update.message.reply_text("Please use the menu to select an option.")


# Add command handlers to the application
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Regex("Go for a Walk|About Bot"), handle_menu_button))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_location_input))

# Set up webhook
webhook_url = f"{WEBHOOK}/{TELEGRAM_BOT_TOKEN}"
application.run_webhook(
    listen='0.0.0.0',
    port=PORT,
    url_path=TELEGRAM_BOT_TOKEN,
    webhook_url=webhook_url
)

