import logging
import datetime
import pytz
import sys
import os
from config import LOGGING_DIR

class Formatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        return dt.astimezone(pytz.timezone("Asia/Krasnoyarsk"))

    def formatTime(self, record, datefmt=None):
        if sys.meta_path is None:
            return ""

        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec="milliseconds")
            except TypeError:
                s = dt.isoformat()
        return s


def setup_logging():
    if not os.path.exists(LOGGING_DIR):
        os.makedirs(os.path.dirname(LOGGING_DIR)) 
    LOGGING_PATH = os.path.join(LOGGING_DIR, 'bot.log')
    file_handler = logging.FileHandler(LOGGING_PATH)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S,%f")
    )

    logging.basicConfig(level=logging.INFO, handlers=[file_handler])

    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.ERROR)
    sqlalchemy_logger.addHandler(file_handler)
    sqlalchemy_logger.propagate = False

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if not isinstance(handler, logging.FileHandler):
            root_logger.removeHandler(handler)
