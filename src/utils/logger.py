import logging

def init_logger(logger=None):
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        if logger is None:
            logger = logging.getLogger(__name__)
        return logger
    except Exception as e:
        print(f"Error initializing logger: {e}")