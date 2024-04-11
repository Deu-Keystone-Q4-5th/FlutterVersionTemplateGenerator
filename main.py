import logging
import sys

import logger_manager


def main():
    manager = logger_manager.LoggerManager()
    logger = manager.get_logger()

    logger.info("Hello World!")

main()