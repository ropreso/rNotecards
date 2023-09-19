"""
does a thing
"""
from tkinter import *
import pandas as pd
import random
import argparse
import shutil
from rNotecards.config import CONFIG_DICT, CONFIG_KEYS
import math
import pyperclip


class RNotecard:
    """
    A single notecard
    """

    def __init__(self, data):
        self.data = data
        self.temp_data = {}

    def add_temp_data(self, key, value):
        """
        Add temporary data to the class instance.

        Parameters:
            key (str): The key to associate the value with.
            value (Any): The value to be stored.

        Returns:
            None
        """
        self.temp_data[key] = value

    def get_temp_data(self, key):
        """
        Get the value associated with the given key from the temporary data.

        Parameters:
            key (str): The key to retrieve the value for.

        Returns:
            Any: The value associated with the key, or None if the key is not found.
        """
        return self.temp_data.get(key, None)

    def calculate_total_perf_score(self):
        """
        Calculate the total performance score.

        This function calculates the total performance score by looping through each level (l1, l2, l3, l4) and
        calculating the temporary score for each level. The temporary score is obtained by retrieving the score from
        the data dictionary using the corresponding key for the level. If the score is NaN, it is set to -20 for l1 or
        the rolling minimum score for the other levels. The rolling minimum score is updated for each level by
        comparing it with the temporary score. The total performance score is then updated by adding the temporary
        score multiplied by a factor of 0.5 raised to the power of (i - 1), where i represents the current level. The
        temporary scores are also stored in a temporary data dictionary for future reference if needed.

        Parameters:
            self (object): The current instance of the class.

        Returns:
            float: The total performance score.
        """
        # Initialize rolling_min and total_perf_score
        rolling_min = float('inf')
        total_perf_score = 0

        # Loop through each level and calculate the temp score and update rolling_min
        for i in range(1, 5):  # For l1, l2, l3, l4
            key = f'l{i}_perf_score'
            temp_key = f'temp_{key}'

            # Get the score from data, if it's NaN set it to -20 for l1 or rolling_min for others
            score = self.data.get(key, float('nan'))
            if math.isnan(score):
                temp_score = -20 if i == 1 else rolling_min
            else:
                temp_score = score

            # Update rolling_min
            rolling_min = min(rolling_min, temp_score)

            # Update total_perf_score
            total_perf_score += temp_score * (0.5 ** (i - 1))

            # Store the temp_score in temp_data for future reference if needed
            self.add_temp_data(temp_key, temp_score)

        # Store the total_perf_score in temp_data
        self.data['total_perf_score'] = total_perf_score


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

    def __init__(self, excel_file_path, backup_file_path):
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
        self.backup_status_label = None
        self.excel_file_path = excel_file_path
        self.backup_file_path = backup_file_path
        self.module_var = None
        self.question_label = None
        self.user_answer = None
        self.answer_entry = None
        self.answer_submitted_window = None
        self.submit_answer_button = None
        self.skip_question_button = None
        self.choose_question_button = None
        self.module_dropdown = None
        self.answer1_score_var = None
        self.answer2_score_var = None
        self.revised_answer_score_var = None
        self.revised_answer_var = None
        self.filtered_indices = []
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

    def save_to_excel(self):
        """
        Save notecard data back to Excel
        """
        with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
            for id_set, rnotecard_set in self.rnotecard_sets_dict.items():
                # Convert the notecard set to a DataFrame
                data = [notecard.data for notecard in rnotecard_set.notecards]
                df = pd.DataFrame(data)

                # Save the DataFrame to an Excel sheet
                sheet_name = f'RN__{id_set}'
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    def flip_card(self):
        """
        Flip a card
        """
        # Remove all widgets from card_window
        for widget in self.card_window.winfo_children():
            widget.destroy()

        if self.current_card.is_front:
            # If the card is currently showing the front, display the back
            Label(self.card_window, text=self.current_card.data.get('back', '')).pack()
            self.current_card.is_front = False
        else:
            # If the card is currently showing the back, display the front
            Label(self.card_window, text=self.current_card.data.get('front', '')).pack()
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

                # Create a new notecard set
                notecard_set = RNotecardSet(id_set)

                # Loop through the rows in the dataframe
                for index, row in df.iterrows():
                    # Create a new notecard with a dictionary to hold all columns
                    notecard = RNotecard({col: row[col] for col in df.columns})
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

        # Create a label for backup status
        self.backup_status_label = Label(self.window, text="Backup created: " + self.backup_file_path)
        self.backup_status_label.pack()

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

        # Dropdown for logic/module selection
        self.module_var = StringVar(self.window)
        self.module_var.set(CONFIG_DICT[CONFIG_KEYS.default_module])  # default value
        self.module_dropdown = OptionMenu(self.window, self.module_var, "Basic", "Interview Prep")
        self.module_dropdown.pack()

    def inspect_deck(self):
        """
        Inspect a deck
        """
        inspect_window = Toplevel(self.window)
        inspect_window.title('Inspect deck')

        if self.selected_deck_id is not None:
            selected_deck = self.rnotecard_sets_dict[self.selected_deck_id]

            for notecard in selected_deck.notecards:
                front_snippet = notecard.data.get('front', ''[:100])  # show first 100 characters, adjust as needed
                back_snippet = notecard.data.get('back', ''[:100])  # show first 100 characters, adjust as needed
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
        Label(self.card_window, text=self.current_card.data.get('front')).pack()

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
        self.module_dropdown.pack_forget()
        self.backup_status_label.pack_forget()

        # Call the main menu
        self.create_main_menu()

    def skip_question(self):
        """
        Resets the rounds_since_tested data value to 0 in the current_card object, saves the data to an Excel file,
        clears all widgets from the window, and creates the main menu.

        Parameters:
            self (SkipQuestion): The SkipQuestion object.

        Returns:
            None
        """
        self.current_card.data['rounds_since_tested'] = 0
        self.save_to_excel()
        for widget in self.window.winfo_children():
            widget.pack_forget()
        self.create_main_menu()

    def filter_questions(self):
        """
        Filters the questions based on a search term and updates the question listbox.

        Parameters:

        Returns:
            None
        """
        search_term = search_var.get().lower()
        self.filtered_indices = [i for i, card in enumerate(self.learn_pile) if
                                 search_term in card.data.get('front', '').lower()]
        question_listbox.delete(0, END)
        for i in self.filtered_indices:
            question_listbox.insert(END, f"{i + 1}. {self.learn_pile[i].data.get('front', '')[:100]}...")

    def choose_question(self):
        """
        Open a new window to choose a question.

        Parameters:

        Returns:
            None
        """
        # noinspection PyGlobalUndefined
        global search_var  # Declare as global for demonstration; better to make it an instance variable

        choose_question_window = Toplevel(self.window)
        choose_question_window.title('Choose a Question')
        choose_question_window.geometry('800x600')  # Set the window size to 800x600

        search_var = StringVar()
        search_entry = Entry(choose_question_window, textvariable=search_var)
        search_entry.pack()

        search_button = Button(choose_question_window, text="Search", command=self.filter_questions)
        search_button.pack()

        # noinspection PyGlobalUndefined
        global question_listbox  # Declare as global for demonstration; better to make it an instance variable
        question_listbox = Listbox(choose_question_window, width=200)  # Set the width of the Listbox
        question_listbox.pack()

        for i, card in enumerate(self.learn_pile):
            question_listbox.insert(END, f"{i + 1}. {card.data.get('front', '')[:100]}...")  # Show first 100 characters

        def on_select_question():
            """
            Selects a question from the question listbox and updates the current card.

            Parameters:

            Returns:
                None
            """
            selected_idx = question_listbox.curselection()
            if selected_idx:
                # Use the filtered_indices list to find the corresponding question in learn_pile
                original_idx = self.filtered_indices[selected_idx[0]]
                self.current_card = self.learn_pile[original_idx]
                choose_question_window.destroy()
                self.question_label.config(text=self.current_card.data.get('front') + "\n")

        select_button = Button(choose_question_window, text="Select", command=on_select_question)
        select_button.pack()

    def create_main_menu(self):
        """
        Create the main menu GUI
        """
        if self.module_var.get() == "Basic":
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
        elif self.module_var.get() == "Interview Prep":
            # Calculate total_perf_score for each RNotecard in self.learn_pile
            for card in self.learn_pile:
                card.calculate_total_perf_score()

            # Find the card with the lowest total_perf_score
            min_score = float('inf')
            self.current_card = None
            for card in self.learn_pile:
                card_score = card.data.get('total_perf_score', float('inf'))
                rounds_since_tested = card.data.get('rounds_since_tested', float('inf'))
                if card_score < min_score and rounds_since_tested > 7:
                    min_score = card_score
                    self.current_card = card

            self.window.geometry("800x600")  # Sets the window size to 800 pixels wide and 600 pixels high
            self.question_label = Label(self.window, text=self.current_card.data.get('front') + "\n", wraplength=750)
            self.question_label.pack()

            # Text widget to accept user input (answer), replacing the previous Entry widget
            self.answer_entry = Text(self.window, wrap="word", width=75, height=25)  # Adjust width and height as needed
            self.answer_entry.pack()

            # Button to submit the answer
            self.submit_answer_button = Button(self.window, text="Submit Answer", command=self.submit_answer)
            self.submit_answer_button.pack()

            # Add the Skip Question button
            self.skip_question_button = Button(self.window, text="Skip Question", command=self.skip_question)
            self.skip_question_button.pack()

            # Add this line where you create your buttons
            self.choose_question_button = Button(self.window, text="Choose Question", command=self.choose_question)
            self.choose_question_button.pack()

    def update_rnotecard_data(self):
        """
        Update the current card and all other cards with the latest data.

        This function updates the current card and all other cards by performing the following steps:
        1. Get the scores for answer1 and answer2.
        2. Get the revised answer.
        3. Update the current card's performance scores by shifting the values.
        4. Update the current card's l1_perf_score with the difference between answer1_score and answer2_score.
        5. Update the current card's back field with the revised answer.
        6. Reset the rounds_since_tested for the current card to 0.
        7. Increment the rounds_since_tested for all other cards by 1.

        Note: This function does not save the changes back to the data source.

        Parameters:
        - None

        Returns:
        - None
        """
        answer1_score = float(self.answer1_score_var.get())
        answer2_score = float(self.answer2_score_var.get())
        revised_answer_score = float(self.revised_answer_score_var.get())
        revised_answer = self.revised_answer_var.get('1.0', 'end')

        # Update the current card
        self.current_card.data['l4_answer1_score'] = self.current_card.data['l3_answer1_score']
        self.current_card.data['l3_answer1_score'] = self.current_card.data['l2_answer1_score']
        self.current_card.data['l2_answer1_score'] = self.current_card.data['l1_answer1_score']
        self.current_card.data['l1_answer1_score'] = answer1_score

        self.current_card.data['l4_answer2_score'] = self.current_card.data['l3_answer2_score']
        self.current_card.data['l3_answer2_score'] = self.current_card.data['l2_answer2_score']
        self.current_card.data['l2_answer2_score'] = self.current_card.data['l1_answer2_score']
        self.current_card.data['l1_answer2_score'] = answer2_score

        self.current_card.data['l4_revised_answer_score'] = self.current_card.data['l3_revised_answer_score']
        self.current_card.data['l3_revised_answer_score'] = self.current_card.data['l2_revised_answer_score']
        self.current_card.data['l2_revised_answer_score'] = self.current_card.data['l1_revised_answer_score']
        self.current_card.data['l1_revised_answer_score'] = revised_answer_score

        self.current_card.data['l4_perf_score'] = self.current_card.data['l3_perf_score']
        self.current_card.data['l3_perf_score'] = self.current_card.data['l2_perf_score']
        self.current_card.data['l2_perf_score'] = self.current_card.data['l1_perf_score']
        self.current_card.data['l1_perf_score'] = answer1_score - revised_answer_score

        self.current_card.data['back'] = revised_answer
        self.current_card.data['rounds_since_tested'] = -1

        # Update all other cards
        for card in self.learn_pile:
            card.data['rounds_since_tested'] += 1

        # Save these changes back to your data source, if needed
        self.save_to_excel()

        for widget in self.window.winfo_children():
            widget.pack_forget()

        self.create_main_menu()

    def submit_answer(self):
        """
        Submit an answer and handle the submitted answer.

        This function creates a new window or frame to display the result of the submitted answer.

        Parameters:
            self (object): The current instance of the class.

        Returns:
            None
        """
        # Logic for handling the submitted answer
        # Then create a new window or frame
        # self.answer_submitted_window = Tk()
        self.question_label.pack_forget()
        self.answer_entry.pack_forget()
        self.submit_answer_button.pack_forget()
        self.skip_question_button.pack_forget()

        self.window.title("Answer Submitted")

        # Initialize StringVar for each entry
        self.answer1_score_var = StringVar()
        self.answer2_score_var = StringVar()
        self.revised_answer_score_var = StringVar()
        self.revised_answer_var = StringVar()

        # Create Entry for Answer 1 Score
        Label(self.window, text="Answer 1 Score:").pack()
        Entry(self.window, textvariable=self.answer1_score_var).pack()

        # Create Entry for Answer 2 Score
        Label(self.window, text="Answer 2 Score:").pack()
        Entry(self.window, textvariable=self.answer2_score_var).pack()

        # Create Entry for Revised Answer Score
        Label(self.window, text="Revised Answer Score:").pack()
        Entry(self.window, textvariable=self.revised_answer_score_var).pack()

        # Create Entry for Revised Answer
        # Label(self.window, text="Revised Answer:").pack()
        # Entry(self.window, textvariable=self.revised_answer_var).pack()
        Label(self.window, text="Revised Answer:").pack()

        # Create a Text widget for multi-line input
        self.revised_answer_var = Text(self.window, wrap='word', width=50,
                                       height=10)  # You can adjust width and height as needed
        self.revised_answer_var.pack()

        # Create Submit Button
        submit_button = Button(self.window, text="Submit Scores and Revised Answer", command=self.update_rnotecard_data)
        submit_button.pack()

        # Display whatever you want here (e.g., "Your answer is correct!")
        label = Label(self.window, text="Push button to copy ChatGPT prompt.")
        label.pack()

        # Button to copy a string to the clipboard
        copy_button = Button(self.window, text="Copy ChatGPT prompt", command=self.copy_to_clipboard)
        copy_button.pack()

    def copy_to_clipboard(self):
        """
         Copy the given string to the clipboard.
         """
        # Replace the placeholders with actual variables
        current_question = self.current_card.data.get('front')
        answer_1 = self.answer_entry.get("1.0", "end-1c")  # Assuming this is how you get Answer 1 from the Text widget
        answer_2 = self.current_card.data.get('back')  # Replace with actual Answer 2

        # Construct the prompt
        prompt = (
            'Please provide an answer like the following: "Answer 1 Score: \$X\$; Answer 2 Score: \$Y\$; \$Revised '
            'Answer Here\$; Revised Answer Score: \$Z\$".  The \$ symbol designates a placeholder.  At the end of '
            'this prompt, you will be given an interview question consistent with that  supplied pdf.  Two answers '
            'will be provided, Answer 1 and Answer 2.  X should be the score between 1 and 10 in terms of the quality '
            'of the answer in the context of a job interview (do not rate down for spelling or grammatical mistakes). '
            ' Y and Z live in the same domain as X.  If X is greater'
            'than Y, then the revised answer should equal Answer 1, and Z will equal X.  If Y is greater than X, '
            'you should attempt to incorporate the personalized elements of X in the revised answer, and you should '
            'ensure Z is at least as large as Y.  Here now is the question and two answers'
            f' Question: {current_question}... Answer 1: {answer_1}...'
            f' Answer 2: {answer_2}'
        )

        pyperclip.copy(prompt)

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
            Label(self.card_window, text=self.current_card.data.get('front', '')).pack()

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


def backup_excel_file(excel_file_path):
    """
    Creates a backup of the specified Excel file.

    Args:
        excel_file_path (str): The path to the Excel file to be backed up.

    Returns:
        None
    """
    backup_file_path = excel_file_path.split('.xlsx')[0] + '_backup.xlsx'
    shutil.copy2(excel_file_path, backup_file_path)
    print(f"Backup created at {backup_file_path}")
    return backup_file_path


def main(excel_file_path: str):
    """
    main method for running the program
    :param excel_file_path:
    """
    backup_file_path = backup_excel_file(excel_file_path)
    app = RNotecardApp(excel_file_path, backup_file_path)
    app.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='excel file path')
    parser.add_argument('excel_file_path', metavar='ExcelFilePath', type=str,
                        help='path of the excel file with notecard worksheets')

    args = parser.parse_args()

    main(args.excel_file_path)
