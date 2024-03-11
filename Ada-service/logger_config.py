import logging


def setup_logger():
    logger = logging.getLogger("main_service_logger")
    logger.setLevel(logging.INFO)

    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.ERROR)

    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    c_handler.setFormatter(c_format)

    logger.addHandler(c_handler)

    return logger
