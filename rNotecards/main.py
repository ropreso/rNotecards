"""
does a thing
"""

from tkinter import messagebox
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
        self.unknown_count_label = None
        self.known_count_label = None
        self.learn_count_label = None
        self.card_window = None
        self.current_card = None
        self.selected_deck_id = None
        self.inspect_button = None
        self.choose_button = None
        self.listbox = None
        self.label = None
        self.excel_file_path = excel_file_path
        self.window = Tk()
        self.window.title('rNotecards')

        # Create a dictionary to store the data from each sheet
        self.rnotecard_sets_dict = {}

        # Load Excel data using pandas
        self.load_excel_data()

        # Define your three piles here, as lists
        self.learn_pile = []
        self.unknown_pile = []
        self.known_pile = []

        # Initialize GUI elements
        self.create_gui()

    def flip_card(self):
        """
        Flip a card
        """
        # Remove all widgets from card_window
        for widget in self.card_window.winfo_children():
            widget.destroy()

        if self.current_card.is_front:
            # If the card is currently showing the front, display the back
            Label(self.card_window, text=self.current_card.back).pack()
            self.current_card.is_front = False
        else:
            # If the card is currently showing the back, display the front
            Label(self.card_window, text=self.current_card.front).pack()
            self.current_card.is_front = True

        # Create a button to mark the card as known
        known_button = Button(self.card_window, text="Mark Known", command=self.mark_known)
        known_button.pack()

        # Create a button to mark the card as unknown
        unknown_button = Button(self.card_window, text="Mark Unknown", command=self.mark_unknown)
        unknown_button.pack()

    def quit_card(self):
        """
        Quit card learning process, returning the card back to learn pile
        """
        self.learn_pile.insert(0, self.current_card)
        self.card_window.destroy()

    def mark_known(self):
        """
        Mark a card as known
        """
        self.known_pile.append(self.current_card)
        self.current_card = None
        self.update_counts()
        self.card_window.destroy()  # close the card window
        if self.learn_pile:  # check if there are still cards in the learn pile
            self.learn()

    def mark_unknown(self):
        """
        Mark a card as unknown
        """
        self.unknown_pile.append(self.current_card)
        self.current_card = None
        self.update_counts()
        self.card_window.destroy()  # close the card window
        if self.learn_pile:  # check if there are still cards in the learn pile
            self.learn()

    def load_excel_data(self):
        """
        Load Excel notecard data
        """
        # Load Excel file
        xls = pd.ExcelFile(self.excel_file_path)

        # Get names of all sheets in the file
        all_sheet_names = xls.sheet_names

        for sheet_name in all_sheet_names:
            # We're looking for sheets that start with 'RN__'
            if sheet_name.startswith('RN__'):
                # Get the id part of the name
                id_set = sheet_name.split('RN__')[1]

                # Read the sheet into a dataframe
                df = pd.read_excel(xls, sheet_name, engine='openpyxl')

                # Make sure column names are all lowercase
                df.columns = map(str.lower, df.columns)

                # Check if both 'front' and 'back' columns exist
                if 'front' in df.columns and 'back' in df.columns:
                    # Create a new notecard set
                    notecard_set = RNotecardSet(id_set)

                    # Loop through the rows in the dataframe
                    for index, row in df.iterrows():
                        # Create a new notecard
                        notecard = RNotecard(row['front'], row['back'])
                        # Add the notecard to the set
                        notecard_set.notecards.append(notecard)

                    # Add the notecard set to the flashcards_data dictionary
                    self.rnotecard_sets_dict[id_set] = notecard_set

    def choose_notecard_set(self, id_set):
        """
        The user chooses a notecard set from the GUI
        :param id_set: The id of the set to choose
        """
        # Clear the learn pile
        self.learn_pile.clear()

        # Add all cards from this id to the learn pile
        self.learn_pile.extend(self.rnotecard_sets_dict[id_set].notecards)

        # Shuffle the learn pile
        random.shuffle(self.learn_pile)

        # Clear the known and unknown piles
        self.known_pile.clear()
        self.unknown_pile.clear()

    # noinspection PyUnusedLocal
    def listbox_select_callback(self, event):
        """
        to inform the inspect deck button which is the selected deck
        :param event:
        """
        selected = self.listbox.curselection()

        if selected:  # if there is a selection
            self.inspect_button.config(state=NORMAL)  # enable the inspect button
            self.selected_deck_id = self.listbox.get(selected)  # store the selected deck id
        else:
            self.inspect_button.config(state=DISABLED)  # disable the inspect button
            self.selected_deck_id = None  # clear the selected deck id

    def create_gui(self):
        """
        Create the GUI
        """
        # Create a label
        self.label = Label(self.window, text="Choose a notecard set to learn:")
        self.label.pack()

        # Create a listbox for the notecard sets
        self.listbox = Listbox(self.window)
        for id_set in self.rnotecard_sets_dict:
            self.listbox.insert(END, id_set)
        self.listbox.bind('<<ListboxSelect>>', self.listbox_select_callback)  # bind the callback
        self.listbox.pack()

        # Create a button to choose the selected notecard set
        self.choose_button = Button(self.window, text="Choose deck", command=self.choose_notecard_set_from_listbox)
        self.choose_button.pack()

        self.inspect_button = Button(self.window, text="Inspect deck", command=self.inspect_deck)
        self.inspect_button.pack()

    def inspect_deck(self):
        """
        Inspect a deck
        """
        inspect_window = Toplevel(self.window)
        inspect_window.title('Inspect deck')

        if self.selected_deck_id is not None:
            selected_deck = self.rnotecard_sets_dict[self.selected_deck_id]

            for notecard in selected_deck.notecards:
                front_snippet = notecard.front[:100]  # show first 100 characters, adjust as needed
                back_snippet = notecard.back[:100]  # show first 100 characters, adjust as needed
                snippet = f"Front: {front_snippet}... Back: {back_snippet}..."
                Label(inspect_window, text=snippet).pack()
        else:
            Label(inspect_window, text="No deck selected.").pack()

    def handle_card(self):
        """
        Handle a single notecard
        """
        # Take a card from the top of the learn pile
        self.current_card = self.learn_pile.pop()

        # Create a new Toplevel window
        self.card_window = Toplevel(self.window)

        # Display the card's front
        Label(self.card_window, text=self.current_card.front).pack()

        # Create a button to flip the card
        flip_button = Button(self.card_window, text="Flip Card", command=self.flip_card)
        flip_button.pack()

        # Create a button to quit learning this card
        quit_button = Button(self.card_window, text="Quit", command=self.quit_card)
        quit_button.pack()

    def repopulate_learn_pile(self, include_known):
        """
        Populate the learn pile with cards that are marked as unknown, or all cards if include_known is True
        """
        self.learn_pile = self.unknown_pile.copy()
        self.unknown_pile = []

        if include_known:
            self.learn_pile += self.known_pile.copy()
            self.known_pile = []

        # shuffle the learn pile
        random.shuffle(self.learn_pile)

        # update counts after populating learn pile
        self.update_counts()

    def customize_piles(self):
        """
        This function allows users to manually move cards between piles
        """
        # This function allows users to manually move cards between piles
        pass

    def choose_notecard_set_from_listbox(self):
        """
        Choose a notecard set from the listbox
        """
        # Get the selected id_set
        id_set = self.listbox.get(ACTIVE)

        # Choose the notecard set
        self.choose_notecard_set(id_set)

        # Remove the current GUI elements
        self.listbox.pack_forget()
        self.choose_button.pack_forget()
        self.inspect_button.pack_forget()
        self.label.pack_forget()

        # Call the main menu
        self.create_main_menu()

    def create_main_menu(self):
        """
        Create the main menu GUI
        """
        self.label = Label(self.window, text="Main Menu")
        self.label.pack()

        self.learn_count_label = Label(self.window, text="Learn count: {}".format(len(self.learn_pile)))
        self.learn_count_label.pack()

        self.known_count_label = Label(self.window, text="Known count: {}".format(len(self.known_pile)))
        self.known_count_label.pack()

        self.unknown_count_label = Label(self.window, text="Unknown count: {}".format(len(self.unknown_pile)))
        self.unknown_count_label.pack()

        learn_button = Button(self.window, text="Learn", command=self.learn)
        learn_button.pack()

        populate_learn_pile_exclude_known_button = Button(self.window, text="Populate Learn Pile (Exclude Known)",
                                                          command=lambda: self.repopulate_learn_pile(False))
        populate_learn_pile_exclude_known_button.pack()

        populate_learn_pile_include_known_button = Button(self.window, text="Populate Learn Pile (Include Known)",
                                                          command=lambda: self.repopulate_learn_pile(True))
        populate_learn_pile_include_known_button.pack()

        customize_button = Button(self.window, text="Customize", command=self.customize_piles)
        customize_button.pack()

        exit_button = Button(self.window, text="Exit", command=self.exit_main_menu)
        exit_button.pack()

    def learn(self):
        """
        Start learning process by displaying the top card from the learn pile
        """
        # Pick the top card from learn pile
        if not self.learn_pile:  # if the learn pile is empty
            messagebox.showinfo("Populate Learn Pile",
                                "Please add cards to the Learn Pile before starting learning.")
            return
        else:
            self.current_card = self.learn_pile.pop(0)
            self.current_card.is_front = True  # Initialize to show the front

            # Create a new window for card learning
            self.card_window = Toplevel(self.window)
            self.card_window.title('Learning Card')

            # Display the card's front
            Label(self.card_window, text=self.current_card.front).pack()

            # Create a button to flip the card
            flip_button = Button(self.card_window, text="Flip", command=self.flip_card)
            flip_button.pack()

            # Create a button to quit learning this card
            quit_button = Button(self.card_window, text="Quit", command=self.quit_card)
            quit_button.pack()

    def update_counts(self):
        """
        updates the pile counts for the notecard sets
        """
        self.learn_count_label.config(text="Learn count: {}".format(len(self.learn_pile)))
        self.known_count_label.config(text="Known count: {}".format(len(self.known_pile)))
        self.unknown_count_label.config(text="Unknown count: {}".format(len(self.unknown_pile)))

    def exit_main_menu(self):
        """
        Exit the main menu
        """
        # Here you can add any logic required before exiting the main menu, like saving state
        self.window.quit()

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
