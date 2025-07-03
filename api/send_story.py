import asyncio
from story_engine import send_story

def handler(event, context):
    asyncio.run(send_story())
    return {
        "statusCode": 200,
        "body": "Joke send!"
    }