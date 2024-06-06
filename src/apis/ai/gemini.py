from dotenv import load_dotenv
import requests
import logging
import os

load_dotenv()

GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')
GEMINI_MODEL =  os.getenv('GEMINI_MODEL')

import google.generativeai as genai

# Initialize the client with your API key
genai.configure(api_key=GEMINI_TOKEN)
model = genai.GenerativeModel(GEMINI_MODEL)

def call_gemini_api(prompt , image):
    if not image:
        response = model.generate_content(prompt)
        return response.text
    
    response = model.generate_content([prompt, image])
    return response.text
    