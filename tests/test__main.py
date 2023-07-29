"""
testing of the config.py script
"""
from rNotecards.config import Config
from rNotecards.constants import PROJECT_ROOT_DIR
from rNotecards.main import RNotecardApp


def test__load_excel_data():
    test_app = RNotecardApp(str(PROJECT_ROOT_DIR / 'tests' / 'data' / 'test__notecards_data.xlsx'))

    expected_keys = ['deck01', 'deck02']
    actual_keys = list(test_app.rnotecard_sets_dict.keys())
    assert actual_keys == expected_keys, f"Keys do not match. Expected {expected_keys}, but got {actual_keys}"

    # Assumed test data
    expected_data = {
        'deck01': [
            ('this is the first entered card from deck01', 'a'),
            ('this is the second entered card from deck01', 'b'),
            ('this is the third entered card from deck01', 'c')
        ],
        'deck02': [
            ('this is the first entered card from deck02', 'a'),
            ('this is the second entered card from deck02', 'b'),
            ('this is the third entered card from deck02', 'c'),
            ('this is the fourth entered card from deck02', 'd')
        ]
        # add more decks if needed
    }

    for key, rnotecard_set in test_app.rnotecard_sets_dict.items():
        # Check the id field
        assert rnotecard_set.id == key, f"For key {key}, expected id {key} but got {rnotecard_set.id}"

        # Check the notecards list
        expected_notecards = expected_data[key]
        actual_notecards = [(notecard.front, notecard.back) for notecard in rnotecard_set.notecards]

        assert \
            actual_notecards == expected_notecards, \
            f"For key {key}, expected notecards {expected_notecards} but got {actual_notecards}"
