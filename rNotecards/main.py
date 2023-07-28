"""
The main python script for the project
"""
from tkinter import *


class RNotecardApp:
    """
    The application for the notecards
    """

    def __init__(self):
        self.window = Tk()
        self.window.title('Flash Card App')

        # Define your three piles here, as lists
        self.learn_pile = []
        self.unknown_pile = []
        self.known_pile = []

        # Load Excel data using pandas
        self.load_excel_data()

        # Initialize GUI elements
        self.create_gui()

    def load_excel_data(self):
        """
        Load Excel data using pandas
        """
        # load Excel data using pandas, find all sheets matching the criteria and load the cards into learn pile
        pass

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


if __name__ == "__main__":
    app = RNotecardApp()
    app.run()
