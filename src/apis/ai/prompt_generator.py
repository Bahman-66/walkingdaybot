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