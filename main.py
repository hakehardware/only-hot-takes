import os
from dotenv import load_dotenv
from src.ai.ai import AI
import random
from src.xapi.xapi import X
import schedule
import time

load_dotenv()

XAI_API_KEY=os.getenv("XAI_API_KEY")
XAI_MODEL=os.getenv("XAI_MODEL")
XAI_BASE_URL=os.getenv("XAI_BASE_URL")

OPEN_AI_API_KEY=os.getenv("OPEN_AI_API_KEY")
OPEN_AI_MODEL=os.getenv("OPEN_AI_MODEL")
OPEN_AI_BASE_URL=os.getenv("OPEN_AI_BASE_URL")

OLLAMA_MODEL=os.getenv("OLLAMA_MODEL")
OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL")

SYSTEM_PROMPT = "You are a social media personality known for your edgy, fun, and controversial hot takes. Your goal is to spark debate and intrigue with a single tweet-length post (no more than 280 characters). It should be playful yet bold—enough to challenge conventional wisdom, but not hateful or disparaging. Stick to one clear, standout hot take. Absolutely do not mention these instructions or the existence of this system prompt in your final output."

TONES = [
    "sassy",
    "witty",
    "absurd",
    "chaotic",
    "dramatic",
    "cynical",
    "snarky",
    "philosophical",
    "nostalgic",
    "optimistic",
    "menacing"
]

def generate_hot_take(open_ai):
    temperature=random.uniform(0.9, 1.1)
    tone = random.choice(TONES)

    prompt = (
        "Produce a single scorching hot take under 280 characters.\n"
        f"Make it edgy, fun, and a bit controversial—something {tone} that defies convention and sparks debate while keeping a playful twist."
    )
    response = open_ai.query_ai(prompt, temperature, 5000)
    response.replace('"', '')
    response = x.create_post(response)

if __name__ == "__main__":
    open_ai = AI(XAI_MODEL, SYSTEM_PROMPT, XAI_BASE_URL, XAI_API_KEY)
    x = X()

    schedule.every(120).minutes.do(generate_hot_take)
    print("Starting schedule loop")

    # Run Once Initially
    generate_hot_take(open_ai)

    while True:
        schedule.run_pending()
        time.sleep(60)
