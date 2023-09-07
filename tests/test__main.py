"""
testing of the config.py script
"""
from rNotecards.config import Config
from rNotecards.constants import PROJECT_ROOT_DIR
from rNotecards.main import RNotecardApp, RNotecard
import shutil
import pandas as pd
import os
import time
import gc


def test__load_excel_data():
    test_app = RNotecardApp(str(PROJECT_ROOT_DIR / 'tests' / 'data' / 'test__notecards_data.xlsx'))

    expected_keys = ['deck01', 'deck02']
    actual_keys = list(test_app.rnotecard_sets_dict.keys())
    assert actual_keys == expected_keys, f"Keys do not match. Expected {expected_keys}, but got {actual_keys}"

    # Assumed test data
    expected_data = {
        'deck01': [
            {'front': 'this is the first entered card from deck01', 'back': 'a'},
            {'front': 'this is the second entered card from deck01', 'back': 'b'},
            {'front': 'this is the third entered card from deck01', 'back': 'c'}
        ],
        'deck02': [
            {'front': 'this is the first entered card from deck02', 'back': 'a'},
            {'front': 'this is the second entered card from deck02', 'back': 'b'},
            {'front': 'this is the third entered card from deck02', 'back': 'c'},
            {'front': 'this is the fourth entered card from deck02', 'back': 'd'}
        ]
        # add more decks if needed
    }

    for key, rnotecard_set in test_app.rnotecard_sets_dict.items():
        # Check the id field
        assert rnotecard_set.id == key, f"For key {key}, expected id {key} but got {rnotecard_set.id}"

        # Check the notecards list
        expected_notecards = expected_data[key]
        actual_notecards = [notecard.data for notecard in rnotecard_set.notecards]

        assert \
            actual_notecards == expected_notecards, \
            f"For key {key}, expected notecards {expected_notecards} but got {actual_notecards}"


def test__save_to_excel():
    # Step 1: Create a copy of the original Excel file for testing
    original_excel_path = str(PROJECT_ROOT_DIR / 'tests' / 'data' / 'test__notecards_data.xlsx')
    temp_excel_path = str(PROJECT_ROOT_DIR / 'tests' / 'data' / 'temp_test__notecards_data.xlsx')
    shutil.copyfile(original_excel_path, temp_excel_path)

    # Step 2: Load the Excel file into an RNotecardApp object
    test_app = RNotecardApp(temp_excel_path)

    # Step 3: Make some changes to the notecards
    new_card = RNotecard({'front': 'new front', 'back': 'new back'})
    test_app.rnotecard_sets_dict['deck01'].notecards.append(new_card)

    # Step 4: Call the save_to_excel method
    test_app.save_to_excel()

    del test_app
    gc.collect()
    # Step 5: Reload the Excel file and verify changes
    with pd.ExcelFile(temp_excel_path) as xls:  # Using 'with' ensures the file is closed after use
        df = pd.read_excel(xls, 'RN__deck01', engine='openpyxl')
        df.columns = map(str.lower, df.columns)

        # Verify that the new card has been added
        assert ("new front", "new back") in zip(df['front'], df['back']), "New card was not saved to Excel"

    # Clean up: Remove the temporary Excel file
    os.remove(temp_excel_path)
