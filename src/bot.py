import os
import logging
import pathlib
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, timedelta
from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

from apis.ai.gemini import call_gemini_api
from apis.ai.huggingface_bart import summarize
from apis.ai.openai import call_openai_api
from apis.ai.prompt_generator import create_weather_prompt
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
user_states = {}

def create_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Go for a Walk", callback_data='1'),
            InlineKeyboardButton("About Bot", callback_data='2')
        ],
        [InlineKeyboardButton("Ask Question", callback_data='3'),],
        [InlineKeyboardButton("Send Image With Caption", callback_data='4'),],
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
        case '3':
            user_states[user_id] = 'awaiting_image'
            await query.message.reply_text("Send your image:", reply_markup=ForceReply(selective=True))
        case _:
            return None
                        
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

        response = call_gemini_api(prompt)
        if response:
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Failed to fetch response from OpenAI API")
    else:
        await update.message.reply_html(
            f"Dear {user.mention_html()}, weather information is missing, please try later.")

async def handle_menu_button(update: Update, context: CallbackContext):
    """Handles user interaction with menu buttons."""
    user_choice = update.message.text.strip()
    user_id = update.effective_user.id

    if user_choice == "Go for a Walk":
        user_states[user_id] = 'awaiting_location'
        await update.message.reply_text("Please provide your location (city name):", reply_markup=ForceReply(selective=True))
    elif user_choice == "Summarize Text":
        user_states[user_id] = 'awaiting_txt'
        await update.message.reply_text("Ask me anything:", reply_markup=ForceReply(selective=True))
    elif user_choice == "About Bot":
        about_bot_text = "This bot helps you with finding the best time for a walk based on the weather forecast. Feel free to explore the options!"
        await update.message.reply_text(about_bot_text)
    else:
        await update.message.reply_text("Invalid option. Please choose from the menu.")

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
    elif user_states.get(user_id) == 'awaiting_image':
        photo_file_id = update.message.photo[-1].file_id
        photo_file = context.bot.get_file(photo_file_id)
        photo_path = f"downloads/{photo_file_id}.png"
        photo_file.download(photo_path)
            
            # Read the photo bytes
        photo_bytes = pathlib.Path(photo_path).read_bytes()
            
            # Prepare the data dictionary
        cookie_picture = {
            'mime_type': 'image/png',
            'data': photo_bytes
        }
        caption = update.message.caption
        
        result = call_gemini_api(caption , cookie_picture)
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
application.add_handler(MessageHandler(filters.TEXT & filters.PHOTO & ~filters.COMMAND, handle_input))
application.add_handler(CallbackQueryHandler(button))

# Set up webhook
webhook_url = f"{WEBHOOK}/{TELEGRAM_BOT_TOKEN}"
application.run_webhook(
    listen='0.0.0.0',
    port=PORT,
    url_path=TELEGRAM_BOT_TOKEN,
    webhook_url=webhook_url
)

