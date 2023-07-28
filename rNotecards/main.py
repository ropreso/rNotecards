"""
does a thing
"""

from tkinter import *
import pandas as pd
import random
import argparse


class RNotecard:
    """
    A single notecard
    """

    def __init__(self, front, back):
        self.front = front
        self.back = back


class RNotecardSet:
    """
    A set of notecards
    """

    def __init__(self, id_set):
        self.id = id_set
        self.notecards = []


class RNotecardApp:
    """
    The application for the notecards
    """

    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.window = Tk()
        self.window.title('Flash Card App')

        # Load Excel data using pandas
        self.load_excel_data()

        # Define your three piles here, as lists
        self.learn_pile = []
        self.unknown_pile = []
        self.known_pile = []

        # Create a dictionary to store the data from each sheet
        self.flashcards_data = {}

        # Initialize GUI elements
        self.create_gui()

    def load_excel_data(self):
        """
        Load Excel notecard data
        """
        # Load Excel file
        xls = pd.ExcelFile(self.excel_file_path)

        # Get names of all sheets in the file
        all_sheet_names = xls.sheet_names

        for sheet_name in all_sheet_names:
            # We're looking for sheets that start with 'notecards_'
            if sheet_name.startswith('notecards_'):
                # Get the id part of the name
                id_set = sheet_name.split('notecards_')[1]

                # Read the sheet into a dataframe
                df = pd.read_excel(xls, sheet_name, engine='openpyxl')

                # Make sure column names are all lowercase
                df.columns = map(str.lower, df.columns)

                # Check if both 'front' and 'back' columns exist
                if 'front' in df.columns and 'back' in df.columns:
                    # Create a new notecard set
                    notecard_set = RNotecardSet(id)

                    # Loop through the rows in the dataframe
                    for index, row in df.iterrows():
                        # Create a new notecard
                        notecard = RNotecard(row['front'], row['back'])
                        # Add the notecard to the set
                        notecard_set.notecards.append(notecard)

                    # Add the notecard set to the flashcards_data dictionary
                    self.flashcards_data[id_set] = notecard_set
                    # Add all cards from this id to the learn pile
                    self.learn_pile.extend(notecard_set.notecards)

        # Shuffle the learn pile
        random.shuffle(self.learn_pile)

    def create_gui(self):
        """
        Create the GUI
        """
        # create the front menu GUI using Tkinter widgets (buttons, labels, lists)
        pass

    def handle_card(self):
        """
        Handle a card
        """
        # This function would be called when the user wants to "learn". It would display a card, let the user flip it,
        # and then mark it as known or unknown, adding it to the respective pile.
        pass

    def repopulate_learn_pile(self, include_known):
        """
        Repopulate the learn pile
        :param include_known:
        """
        # This function would be called to repopulate the learn pile from the unknown (and maybe known) piles,
        # shuffling the cards.
        pass

    def customize_piles(self):
        """
        This function allows users to manually move cards between piles
        """
        # This function allows users to manually move cards between piles
        pass

    def run(self):
        """
        This function runs the GUI
        """
        self.window.mainloop()


def main(excel_file_path: str):
    """
    main method for running the program
    :param excel_file_path:
    """
    app = RNotecardApp(excel_file_path)
    app.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='excel file path')
    parser.add_argument('excel_file_path', metavar='EFP', type=str,
                        help='path of the excel file with notecard worksheets')

    args = parser.parse_args()

    main(args.excel_file_path)
