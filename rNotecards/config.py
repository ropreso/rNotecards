"""
deals with the configuration of the program
"""
import yaml
from collections import namedtuple

from rNotecards.constants import PROJECT_ROOT_DIR


class Config:
    """Handles loading and accessing configuration values."""

    def __init__(self, config_file_path):
        """Initialize the Config class.

        Args:
            config_file_path (str): Path to the configuration file.
        """
        self.config = self.load_config(config_file_path)

    @staticmethod
    def load_config(file_path):
        """Load the configuration file.

        Args:
            file_path (str): Path to the configuration file.

        Returns:
            dict: Configuration values.
        """
        with open(file_path, 'r') as stream:
            config = yaml.safe_load(stream)

        # Now, dynamically create the ConfigKeys namedtuple with the keys from the config
        ConfigKeys = namedtuple('ConfigKeys', config.keys())
        # noinspection PyPep8Naming,PyShadowingNames
        CONFIG_KEYS = ConfigKeys(*config.keys())

        # Replace placeholders with actual values
        for key, value in config.items():
            if isinstance(value, str):
                config[key] = value.format(PROJECT_ROOT_DIR=PROJECT_ROOT_DIR)

        return config, CONFIG_KEYS

    def get(self, key):
        """Get a configuration value.

        Args:
            key (str): Configuration key.

        Returns:
            str: Configuration value.
        """
        return self.config.get(key)


CONFIG_PATH = PROJECT_ROOT_DIR / 'configuration' / 'config.yaml'

CONFIG_DICT, CONFIG_KEYS = Config.load_config(str(CONFIG_PATH))
