# Author: p1n93r
# Date  : 2021/01/24

import os
import time
import logging
import logging.handlers


LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
LOG_DIR = "logs"
LOG_LEVEL = logging.INFO


class Logger:
    def __init__(self):
        self.logger = logging.getLogger("riskmon")
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)
        timestamp = time.strftime("%Y_%m_%d", time.localtime())
        log_filename = "{}.log".format(timestamp)
        log_filepath = os.path.join(LOG_DIR, log_filename)
        formatter = logging.Formatter(LOG_FORMAT, '%Y-%m-%d %H:%M:%S')

        log_handler = logging.handlers.RotatingFileHandler(filename=log_filepath, maxBytes=1024*1024*10, backupCount=5)
        log_handler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setFormatter(formatter)

        self.logger.addHandler(log_handler)
        self.logger.addHandler(console)

        self.logger.setLevel(LOG_LEVEL)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)


logger = Logger()
