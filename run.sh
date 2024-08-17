#!/bin/sh

# Find the Python interpreter path
PYTHON_PATH=$(which python3)

# Use the found Python path to run the script
"$PYTHON_PATH" main.py "$@"
