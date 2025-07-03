import asyncio
from flask import Flask
from dotenv import load_dotenv
from main import send_story

load_dotenv()
app = Flask(__name__)

@app.route('/')
def home():
    asyncio.run(send_story())
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'