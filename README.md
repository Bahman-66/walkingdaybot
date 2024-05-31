# Weather Walking Bot

This Telegram bot helps you determine the best time to go for a walk based on weather data. It uses the AccuWeather API to fetch weather data and the OpenAI API to analyze it.

## Features

- **Get Walk Recommendation:** Users can get the best time for a walk based on the weather data using the `/walk` command.
- **Daily Limits:** Each user has a maximum of 5 requests per day.

## Setup

1. **Clone the repository:**

   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment and activate it:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Create a `.env` file with your API keys:**

   ```sh
   touch .env
   ```

   Add the following lines to the `.env` file:

   ```
   OPENAI_API_KEY=your_openai_api_key
   WEATHER_API_KEY=your_accuweather_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   PORT=your_port  # e.g., 8443
   WEBHOOK=your_webhook_url  # e.g., https://yourdomain.com/webhook
   MODEL=your_openai_model  # e.g., text-davinci-003
   ```

5. **Run the bot:**
   ```sh
   python bot.py
   ```

## Usage

### Example

1. **Start the Bot:**
   /start

You will then receive a menu with options to get a walk recommendation or to learn more about the bot.

2. **Get Walk Recommendation:**

Select "Go for a Walk" from the menu.

## Notes

- Ensure you have only one instance of the bot running to avoid conflicts.
- The bot uses webhooks to receive updates for better efficiency.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
