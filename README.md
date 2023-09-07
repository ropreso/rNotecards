# rNotecards

## Project Description

rNotecards is a Python-based graphical study tool that helps users memorize information using a flashcard system. The
application implements the principles of active recall and spaced repetition, providing an efficient way to learn and
retain information.

## Key Features

1. Load Data from Excel: The application allows users to load flashcards from an Excel file. Each worksheet in the file
   represents a separate flashcard set.
2. Three Piles System: The application organizes flashcards into three categories: learn, known, and unknown. The learn
   pile is for cards currently being studied, the known pile for cards that the user has successfully memorized, and the
   unknown pile for cards that the user has not yet mastered.
3. Study Mode: The application presents flashcards from the learn pile to the user, who can choose to flip the card to
   see the answer. After viewing the answer, the user can mark the card as known or unknown, moving it to the
   appropriate pile.
4. Repopulate Learn Pile: The learn pile can be repopulated from the unknown and known piles.
5. Customize Piles: The application allows users to manually move cards between piles, providing flexibility in managing
   study materials.

## Installation

1. Program is only tested as working on Python 3.10, but you can try on other versions.
2. git clone https://github.com/ropreso/rNotecards.git /path/to/destination-folder.
3. Create virtual environment and source it.
4. python3 /path/to/destination-folder/setup.py

