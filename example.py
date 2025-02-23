from src.xapi.xapi import X
from src.logger import logger
from datetime import datetime

if __name__ == "__main__":
    x = X()
    # Get the current local time
    current_time_local = datetime.now()

    # Format the time in a friendly string format (e.g., "2025-02-23 14:30:00")
    formatted_time = current_time_local.strftime("%Y-%m-%d %H:%M:%S")
    response = x.create_post(f"Hello World, the current time is {formatted_time}!")