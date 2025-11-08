import logging
import sys

from loguru import logger


# Bridge standard logging to loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except Exception:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
logger.remove()
logger.add(sys.stderr, level="INFO", backtrace=True, diagnose=False)
