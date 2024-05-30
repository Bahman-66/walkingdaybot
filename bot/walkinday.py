import requests
import json
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace with your actual API keys

# Function to fetch weather data from AccuWeather API
def fetch_weather_data(location_id):
    base_url = "http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/"
    query_params = {
        "apikey": api_key_weather,
        "metric": "true"
    }
    response = requests.get(f"{base_url}{location_id}", params=query_params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch weather data:", response.status_code)
        return None

# Function to interact with OpenAI API
def call_openai_api(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": prompt}
        ],
        "temperature": 1,
        "max_tokens": 256,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch response from OpenAI API:", response.status_code)
        return None

async def walk(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /walk is issued."""
    # Fetch weather data
    location_id = "30332"
    weather_data = fetch_weather_data(location_id)

    if weather_data:
        # Prepare input for the model
        prompt = "Analyze the following weather data and determine the best time for a walk between 8 AM and 9 PM:\n\n"
        prompt += "Weather Forecast:\n"
        for hour in weather_data:
            prompt += f"- Time: {hour['DateTime']}\n"
            prompt += f"  - Temperature: {hour['Temperature']['Value']}°C\n"
            prompt += f"  - Weather Condition: {hour['IconPhrase']}\n"
            prompt += f"  - Probability of Precipitation: {hour['PrecipitationProbability']}%\n\n"

        prompt += "Based on the weather forecast, it is recommended to avoid walking during periods of high temperature or heavy rain, and prefer cooler or less rainy periods.\n"
        prompt += "What is the best time for a walk?"

        # Make request to GPT-4o API with the correct parameters
        response = call_openai_api(prompt)

        if response:
            # Extract and print the response from the API
            user = update.effective_user
            print(user.mention_html())
            await update.message.reply_html(
                response['choices'][0]['message']['content'].replace("user", user.mention_html()),
                reply_markup=ForceReply(selective=True),
            )
        else:
            await update.message.reply_text("Failed to fetch response from OpenAI API")

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('Help!')

async def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(api_bot_key).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("walk", walk))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
