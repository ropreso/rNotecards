"""
constants.py

This module defines the constants used across the project.

Constants:
----------
PROJECT_ROOT_DIR : pathlib.Path
    The root directory of the project.
"""
from pathlib import Path
import socket

# The root directory of the project
PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent
LOCAL_IP = socket.gethostbyname(socket.gethostname())
