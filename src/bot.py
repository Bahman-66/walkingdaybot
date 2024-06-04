import os
import logging
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, timedelta
from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

from apis.ai.gemini import call_gemini_api
from apis.ai.huggingface_bart import summarize
from apis.ai.openai import call_openai_api
from apis.ai.prompt_generator import create_weather_prompt, generate_stock_prompt
from apis.data.finance import get_stock_data
from apis.data.weather import fetch_location_id, fetch_weather_data

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

user_requests = defaultdict(lambda: {'count': 0, 'timestamp': datetime.now()})

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PORT = int(os.getenv('PORT', 8443))
WEBHOOK = os.getenv('WEBHOOK')

# Initialize application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Global dictionary to store user requests and location IDs
user_requests = {}
user_location_ids = {}
user_finance_ids = {}
user_states = {}

def create_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Go for a Walk", callback_data='1'),
            InlineKeyboardButton("About Bot", callback_data='2')
        ],
        [InlineKeyboardButton("Ask Question", callback_data='3'),],
        [InlineKeyboardButton("Tech Stock Update", callback_data='4'),],
    ]

    return InlineKeyboardMarkup(keyboard)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    #user_choice = update.message.text.strip()
    user_id = update.effective_user.id

    match query.data:
        case '1':
            user_states[user_id] = 'awaiting_location'
            await query.message.reply_text("Please provide your location (city name):", reply_markup=ForceReply(selective=True))
        case '2':
            about_bot_text = "This bot helps you with your day to day needs. Feel free to explore the options!"
            await query.edit_message_text(about_bot_text)
        case '3':
            user_states[user_id] = 'awaiting_txt'
            await query.message.reply_text("Ask me anything:", reply_markup=ForceReply(selective=True))
        case '4':
            user_states[user_id] = 'awaiting_finance'
            await query.message.reply_text("Please provide company stock symbol (example AAPL):", reply_markup=ForceReply(selective=True))
        case _:
            return None
                        
async def walk(update: Update, context: CallbackContext):
    """Handles the /walk command (replace with your existing implementation)"""
    user = update.effective_user
    user_id = user.id

    logging.info(f"Walk: {user.mention_html()}")

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

        response = call_gemini_api(prompt)
        if response:
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Failed to fetch response from OpenAI API")
    else:
        await update.message.reply_html(
            f"Dear {user.mention_html()}, weather information is missing, please try later.")

async def finance(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id

    logging.info(f"Finance: {user.mention_html()}")

    # Ensure user has a location ID set
    if user_id not in user_finance_ids:
        await update.message.reply_html(
            f"Dear {user.mention_html()}, please set your stock <stock_name>.",
            reply_markup=ForceReply(selective=True),
        )
        return

    fiance_symbol = user_finance_ids[user_id]
    finance_data = get_stock_data(fiance_symbol)

    if finance_data:
        # Prepare input for the model (replace with your existing logic)
        stock_data = create_weather_prompt(finance_data)

        prompt = generate_stock_prompt(stock_data)
        if prompt:
            response = call_gemini_api(prompt)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Failed to fetch response from ALPHA API")
    else:
        await update.message.reply_html(
            f"Dear {user.mention_html()}, weather information is missing, please try later.")

async def handle_input(update: Update, context: CallbackContext):
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
    elif user_states.get(user_id) == 'awaiting_txt':
        txt = update.message.text.strip()
        result = call_gemini_api(txt)

        if result:
            user_states[user_id] = None  # Reset user state
            await update.message.reply_text(result)
        else:
            await update.message.reply_text("Could not summarized.")
    else:
        await update.message.reply_text("Please use the menu to select an option.")

async def start(update: Update, context: CallbackContext):
    """Sends a welcome message with the menu keyboard."""
    await update.message.reply_text('Please choose an option:', reply_markup=create_menu_keyboard())

# Add command handlers to the application
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
application.add_handler(CallbackQueryHandler(button))

# Set up webhook
webhook_url = f"{WEBHOOK}/{TELEGRAM_BOT_TOKEN}"
application.run_webhook(
    listen='0.0.0.0',
    port=PORT,
    url_path=TELEGRAM_BOT_TOKEN,
    webhook_url=webhook_url
)

