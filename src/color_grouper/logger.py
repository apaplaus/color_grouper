import logging

LEVEL = logging.DEBUG


def setup_logger(name):
    handler = logging.StreamHandler()
    handler.setLevel(LEVEL)
    logger = logging.getLogger(name)
    logger.setLevel(LEVEL)
    logger.addHandler(handler)
    
    return logger
    