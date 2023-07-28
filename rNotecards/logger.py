"""
Handles the logging for the program
"""
import logging
from rNotecards.config import CONFIG_DICT, CONFIG_KEYS


class Logger:
    """
    Logger class to assist with logging
    """

    def __init__(self, log_file_full_path, log_level_file, log_level_console):
        self.logger = self.setup_logger(log_file_full_path, log_level_file, log_level_console)

    @staticmethod
    def setup_logger(log_file_full_path, log_level_file, log_level_console):
        """
        sets up the logger for the module
        """
        # Create a file handler to log to a file
        file_handler = logging.FileHandler(log_file_full_path)
        file_handler.setLevel(log_level_file)

        # Create a console handler to log to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level_console)

        # Create a formatter for the log messages
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Set the formatter for the handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Get the root logger and add the handlers
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        return root_logger


LOGGER = Logger.setup_logger(
    CONFIG_DICT[CONFIG_KEYS.log_file_full_path], getattr(logging, CONFIG_DICT[CONFIG_KEYS.log_level_file]),
    getattr(logging, CONFIG_DICT[CONFIG_KEYS.log_level_console])
)
