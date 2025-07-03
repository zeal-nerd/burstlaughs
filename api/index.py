import asyncio
from flask import Flask
from dotenv import load_dotenv
from main import send_story

load_dotenv()
app = Flask(__name__)

@app.route('/')
def index():
    asyncio.run(send_story())
    return 'Job done!'
