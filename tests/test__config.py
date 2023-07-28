"""
testing of the config.py script
"""
from rNotecards.config import Config
from rNotecards.constants import PROJECT_ROOT_DIR


def load_test_config():
    """
    loads a test configuration for program testing
    """
    test_config_path = \
        PROJECT_ROOT_DIR / 'tests' / 'configuration' / \
        'config__valid_01.yaml'

    return Config.load_config(str(test_config_path))


def test__load_config_path():
    test_config_dict, test_config_keys = load_test_config()

    # First test
    assert test_config_dict[test_config_keys.log_level_file] == \
           'DEBUG'


def test__load_config_no_braces():
    test_config_dict, test_config_keys = load_test_config()

    # Second test
    for key, value in test_config_dict.items():
        assert "{" not in str(value), f"{key} contains a '{'{'}'"
        assert "}" not in str(value), f"{key} contains a '{'}'}'"
