#!/bin/sh

# Find the Python interpreter path
PYTHON_PATH=$(which python3)

# PID file location
PID_FILE="/tmp/monitoring_pid"

# Function to check if -s is in the arguments
background_run_monitoring=false
for arg in "$@"
do
    if [ "$arg" = "-s" ]; then
        background_run_monitoring=true
        break
    elif [ "$arg" = "-k" ]; then
        # Stop monitoring if -k is passed
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            echo "Stopping monitoring process with PID $PID."
            kill "$PID" && rm "$PID_FILE"
        else
            echo "No monitoring process found to stop."
        fi
        exit 0
    fi
done

# Use the found Python path to run the script
if $background_run_monitoring; then
    echo "Running in background."
    "$PYTHON_PATH" main.py "$@" > /dev/null 2>&1 &
    echo $! > "$PID_FILE"  # Store the PID
else
    "$PYTHON_PATH" main.py "$@"
fi
