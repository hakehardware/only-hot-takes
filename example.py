from src.xapi.xapi import X
from src.logger import logger
import time

if __name__ == "__main__":
    x = X()
    logger.info("Posting to X")
    success = False
    while not success:
        response = x.create_post("Hello World!")
        if response == "success": continue
        elif response == "Not Authorized":
            print("App not authorized, will retry in 60 seconds")
        time.sleep(60)