import logging
import sys


def setup_logger():
    logger = logging.getLogger("event_management_crm")
    logger.propagate = False
    logger.setLevel(logging.INFO)

    # create a handler to write to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # create a formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # add the handler to the logger
    logger.addHandler(handler)

    return logger


logger = setup_logger() 