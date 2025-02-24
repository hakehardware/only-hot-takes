import os
from dotenv import load_dotenv
from src.ai.ai import AI
import random
from src.xapi.xapi import X
import schedule
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

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

XAI_API_KEY=os.getenv("XAI_API_KEY")
XAI_MODEL=os.getenv("XAI_MODEL")
XAI_BASE_URL=os.getenv("XAI_BASE_URL")

OPEN_AI_API_KEY=os.getenv("OPEN_AI_API_KEY")
OPEN_AI_MODEL=os.getenv("OPEN_AI_MODEL")
OPEN_AI_BASE_URL=os.getenv("OPEN_AI_BASE_URL")

OLLAMA_MODEL=os.getenv("OLLAMA_MODEL")
OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL")

SYSTEM_PROMPT = (
    "You are a social media personality known for your edgy, fun, and controversial hot takes.\n "
    "Your goal is to spark debate and intrigue with a single tweet-length post (no more than 280 characters).\n "
    "It should be playful yet bold—enough to challenge conventional wisdom, but not hateful or disparaging. \n"
    "Stick to one clear, standout hot take."
)

def generate_hot_take(open_ai, x_api):
    """Generate and post a hot take with error handling."""
    try:
        temperature = random.uniform(0.9, 1.1)
        tone = random.choice(TONES)
        
        prompt = (
            "Produce a single scorching hot take under 280 characters.\n"
            f"Make it edgy, fun, and a bit controversial—something {tone} that "
            "defies convention and sparks debate while keeping a playful twist."
        )
        
        response = open_ai.query_ai(prompt, temperature, 5000)
        if not response:
            logger.error("No response from AI")
            return None
            
        # Clean and validate response
        cleaned_response = response.strip().replace('"', '')
        if len(cleaned_response) > 280:
            logger.warning("Response too long, not posting")
            return False
                    
        post_result = x_api.create_post(cleaned_response)
        logger.info(f"Successfully posted: {cleaned_response}")
        return post_result
        
    except Exception as e:
        logger.error(f"Error generating hot take: {str(e)}")
        return None


def main():
    """Main application loop with proper initialization and shutdown."""
    try:
        # Initialize APIs
        open_ai = AI(
            OPEN_AI_MODEL,
            SYSTEM_PROMPT,
            OPEN_AI_BASE_URL,
            OPEN_AI_API_KEY
        )
        x_api = X()

        # Schedule job with proper argument passing
        schedule.every(120).minutes.do(generate_hot_take, open_ai=open_ai, x_api=x_api)
        logger.info("Starting schedule loop")

        # Initial run
        generate_hot_take(open_ai, x_api)
        
        # Main loop with graceful shutdown
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                logger.info("Stopping")
                break
                
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
