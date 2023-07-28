"""
testing of the config.py script
"""
from rNotecards.config import Config
from rNotecards.constants import PROJECT_ROOT_DIR
from rNotecards.main import RNotecardApp


def test__load_config_path():
    test_app = RNotecardApp(PROJECT_ROOT_DIR / 'tests' / 'data' / 'test__notecards_data.xlsx')
    print(test_app)
