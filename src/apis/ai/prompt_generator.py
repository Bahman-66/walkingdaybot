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

def generate_stock_prompt_with_full_data(stock_data):
    # Extract meta data
    meta_data = stock_data['Meta Data']
    symbol = meta_data['2. Symbol']
    last_refreshed = meta_data['3. Last Refreshed']
    timezone = meta_data['5. Time Zone']

    # Extract time series data
    time_series = stock_data['Time Series (Daily)']
    
    # Initialize variables to calculate averages and other stats
    total_days = len(time_series)
    total_volume = 0
    total_closing_price = 0
    high_prices = []
    low_prices = []
    closing_prices = []
    volume_data = []

    # Process each data point
    for date, data in time_series.items():
        high_prices.append(float(data['2. high']))
        low_prices.append(float(data['3. low']))
        closing_prices.append(float(data['4. close']))
        volume_data.append(int(data['5. volume']))
        total_closing_price += float(data['4. close'])
        total_volume += int(data['5. volume'])

    # Calculate averages
    average_volume = total_volume / total_days
    average_closing_price = total_closing_price / total_days

    # Most recent data point
    most_recent_date = list(time_series.keys())[0]
    most_recent_data = time_series[most_recent_date]

    # Previous day's data
    previous_date = list(time_series.keys())[1]
    previous_data = time_series[previous_date]

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
        f"\n"
        f"Previous Day's Data ({previous_date}):\n"
        f"Open: {previous_data['1. open']}\n"
        f"High: {previous_data['2. high']}\n"
        f"Low: {previous_data['3. low']}\n"
        f"Close: {previous_data['4. close']}\n"
        f"Volume: {previous_data['5. volume']}\n"
        f"\n"
        f"Summary of Last {total_days} Trading Days:\n"
        f"Average Closing Price: {average_closing_price:.2f}\n"
        f"Highest Price: {max(high_prices):.2f} on {most_recent_date}\n"
        f"Lowest Price: {min(low_prices):.2f} on {most_recent_date}\n"
        f"Average Volume: {average_volume:.2f}\n"
        f"\n"
        f"Questions:\n"
        f"1. How does the most recent closing price compare to the previous day's closing price?\n"
        f"2. What could be the reason for the observed high and low prices on the most recent trading day?\n"
        f"3. How does the trading volume on the most recent day compare to the average volume over the past week?\n"
        f"4. Are there any significant news or events that could have influenced the stock price on the most recent trading day?\n"
        f"5. Based on the recent trend, what are your predictions for the stock's performance in the near future?\n"
        f"6. How does the average closing price over the past {total_days} days compare to the current closing price?\n"
        f"7. What factors could have contributed to the highest and lowest prices observed in the given period?\n"
        f"8. Is there a pattern in the volume data that correlates with price changes?\n"
    )

    return prompt