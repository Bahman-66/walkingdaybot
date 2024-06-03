from gradio_client import Client
from dotenv import load_dotenv
import os

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
HUGGINGFACE_MODEL =  os.getenv('HUGGINGFACE_MODEL')

client = Client(HUGGINGFACE_MODEL, hf_token=HUGGINGFACE_TOKEN)

def summarize(txt):
    return client.predict(
                text=txt,
                num_beams=4,
                api_name="/predict", 
        )
