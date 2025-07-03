import asyncio
import logging
from os import getenv

from random import choice

import httpx
from aiogram import Bot

BOT_TOKEN = getenv('BOT_TOKEN')
GEMINI_API_KEY = getenv('GEMINI_API_KEY')
GOOGLE_API_ENDPOINT = getenv('GOOGLE_API_ENDPOINT')
CHANNEL_ID = getenv('CHANNEL_ID')

class StoryGenerator(httpx.AsyncClient):
    SEED = {
        # Joke topic/context categories
        "context": {
            "programming": [
                "off-by-one error", "null pointer", "merge conflict", "infinite loop", 
                "spaghetti code", "debugging", "rubber ducking", "syntax error",
                "unreachable code", "variable shadowing", "refactoring", "callback hell"
            ],

            "tech-lifestyle": [
                "dark mode addiction", "coffee dependency", "tab hoarding", "burnout",
                "remote work", "daily standups", "tech memes", "hackathons",
                "zoom fatigue", "keyboard warriors", "wearing hoodies all year"
            ],

            "tools & platforms": [
                "Linux terminal", "GitHub", "Stack Overflow", "VS Code", 
                "Jira tickets", "Docker", "ChatGPT", "npm install",
                "CI/CD pipeline", "Firebase", "Postman", "Homebrew"
            ],

            "AI & ML": [
                "hallucinating AI", "data leakage", "GPT everywhere", 
                "overfitting", "training loop", "fine-tuning", 
                "model bias", "data cleaning", "prompt engineering", "tensorboard"
            ],

            "startups & funding": [
                "burn rate", "unicorn status", "pitch deck", "runway", 
                "seed round", "tech bros", "pivoting", "stealth mode",
                "disrupting the industry", "MVP with bugs"
            ],

            "web development": [
                "CSS debugging", "responsive design", "React re-renders", 
                "Tailwind arguments", "npm breaking builds", "JS fatigue",
                "cross-browser bugs", "web3 hype", "frontend/backend beef"
            ],

            "computer science": [
                "big O notation", "hash collisions", "deadlocks", 
                "recursion", "heap vs stack", "race condition", 
                "binary search", "graph traversal", "design patterns", "state machines"
            ]
        },

        # Joke delivery personalities (new!)
        "personality": [
            "a sarcastic Gen-Z Twitter comedian",
            "a dad-joke-loving backend developer",
            "a sassy frontend engineer who's overworked and over it",
            "a motivational tech influencer who thinks memes are therapy",
            "a terminal-only Linux guy with too many opinions",
            "a caffeine-fueled junior dev trying to impress seniors",
            "an AI that thinks it's funny (but isn't... or is it?)",
            "a tech bro who just discovered irony",
            "a burnt-out startup founder who's secretly hilarious",
            "a CTO doing stand-up at a tech meetup"
        ]
    }


    def __init__(self, key: str):
        headers = {
            "x-goog-api-key": f"{key}",
            "Content-Type": "application/json"
        }
        super().__init__(headers=headers)

    def _get_seed(self) -> tuple:
        context = choice(list(self.SEED.keys()))
        word = choice(self.SEED[context])
        return context, word

    def _get_prompt(self) -> list:
        context_key = choice(list(self.SEED["context"].keys()))
        topic = choice(self.SEED["context"][context_key])
        personality = choice(self.SEED["personality"])

        prompt = (
            f"You're {personality}. Write a clever, short, and hilarious joke about '{topic}' "
            f"within the theme of '{context_key}'. Make it relatable to tech people. "
            f"Use emojis where appropriate for emotion. End with two newlines and a few fitting hashtags. "
            f"Only return the joke content — no preamble or explanation."
        )

        return [{"role": "user", "parts": [{"text": prompt}]}]




    async def generate_joke(self) -> str:
        payload = {
            "contents": self._get_prompt(),
            "generationConfig": {
                "temperature": 0.9,           # Higher = more creative
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 200
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": 2
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": 2
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": 2
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": 2
                }
            ]
        }

        response = await self.post(
            url=GOOGLE_API_ENDPOINT,
            json=payload
        )

        response.raise_for_status()
        result = response.json()

        try:
            return result['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "Oops! I couldn’t come up with a joke this time. 🤷‍♂️"

async def send_story():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(BOT_TOKEN)
    story_gen = StoryGenerator(GEMINI_API_KEY)

    story = await story_gen.generate_joke()
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=story
    )

    await bot.session.close()
    await story_gen.aclose()


if __name__ == '__main__':
    asyncio.run(send_story())
