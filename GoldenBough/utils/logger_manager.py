from datetime import datetime
import logging
import os
import sys


def _createDirectory() :
    if not os.path.isdir("../../logs"):
        os.mkdir("../../logs")


class LoggerManager:
    __logger = logging.getLogger("test")

    def __new__(cls):
        if (not hasattr(cls, 'instance')):
            cls.instance = super(LoggerManager, cls).__new__(cls)
            cls.instance.__set_logger()

        return cls.instance;

    def __set_logger(self):
        _createDirectory()
        self.__logger.setLevel(logging.DEBUG)
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(
            logging.Formatter(fmt='%(asctime)s %(levelname)s:%(message)s',
                              datefmt='%m/%d/%Y %I:%M:%S %p'))
        self.__logger.addHandler(stdout_handler)

        stderr_handler = logging.StreamHandler(stream=sys.stderr)
        stderr_handler.setLevel(logging.ERROR)
        stderr_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s:%(message)s',
                                    datefmt='%m/%d/%Y %I:%M:%S %p'))
        self.__logger.addHandler(stderr_handler)
        file_handler = logging.FileHandler("logs/" + str(datetime.now().date()) + ".log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s:%(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p'))
        self.__logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        return self.__logger
