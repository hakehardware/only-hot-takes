from src.xapi.xapi import X
from src.logger import logger


if __name__ == "__main__":
    x = X()
    logger.info("Posting to X")
    x.create_post("Hello World!")
