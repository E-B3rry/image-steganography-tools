# Internal modules
import logging


def configure_logging():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_logger(name: str):
    return logging.getLogger(name)
