
import logging

def get_logger(log_level):
    logger = logging.getLogger('main')
    logger.setLevel(log_level)
    console_logger = logging.StreamHandler()
    console_logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    console_logger.setFormatter(formatter)
    logger.addHandler(console_logger)
    return logger
