from dateutil import parser 

def format_time(datetime_str):
    """Converts ISO 8601 date-time string to a more human-friendly time format."""
    dt = parser.parse(datetime_str)
    return dt.strftime("%-I %p") 

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

def generate_stock_prompt(stock_data):
    # Extract meta data
    meta_data = stock_data['Meta Data']
    symbol = meta_data['2. Symbol']
    last_refreshed = meta_data['3. Last Refreshed']
    timezone = meta_data['5. Time Zone']

    # Extract time series data
    time_series = stock_data['Time Series (Daily)']
    
    # Extract the most recent data point
    most_recent_date = list(time_series.keys())[0]
    most_recent_data = time_series[most_recent_date]
    
    # Generate the prompt
    prompt = (
        f"Stock Symbol: {symbol}\n"
        f"Last Refreshed: {last_refreshed}\n"
        f"Time Zone: {timezone}\n"
        f"\n"
        f"Most Recent Data ({most_recent_date}):\n"
        f"Open: {most_recent_data['1. open']}\n"
        f"High: {most_recent_data['2. high']}\n"
        f"Low: {most_recent_data['3. low']}\n"
        f"Close: {most_recent_data['4. close']}\n"
        f"Volume: {most_recent_data['5. volume']}\n"
        f"Questions:\n"
        f"1. How does the most recent closing price compare to the previous day's closing price?\n"
        f"2. What could be the reason for the observed high and low prices on the most recent trading day?\n"
        f"3. How does the trading volume on the most recent day compare to the average volume over the past week?\n"
        f"4. Are there any significant news or events that could have influenced the stock price on the most recent trading day?\n"
        f"5. Based on the recent trend, what are your predictions for the stock's performance in the near future?\n"
    )

    return prompt