from dotenv import load_dotenv
import requests
import logging
import os

load_dotenv()

GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')

import google.generativeai as genai

# Initialize the client with your API key
genai.configure(api_key=GEMINI_TOKEN)
model = genai.GenerativeModel('gemini-1.5-flash')

def call_gemini_api(prompt):
    response = model.generate_content(prompt)
    return response.text
    