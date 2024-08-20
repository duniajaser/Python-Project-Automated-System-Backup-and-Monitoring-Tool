#!/bin/sh

PYTHON_PATH=$(which python3)

# Function to check if -s or -b is in the arguments
background_run_monitoring=false
backup_path=""

for arg in "$@"
do
    case "$arg" in
        -s | -b)
            background_run_monitoring=true
            ;;
        -k)
            # Stop monitoring if -k is passed
            PIDS=$(ps aux | grep '[m]ain.py -s' | awk '{print $2}')
            if [ -n "$PIDS" ]; then
                echo "Stopping monitoring processes..."
                for PID in $PIDS; do
                    echo "Killing PID $PID"
                    kill -15 "$PID"  # Using numeric signal code for SIGTERM
                done
            else
                echo "No monitoring processes found to stop."
            fi
            exit 0
            ;;
        -u)
            shift
            backup_path="$1"  # Properly quote the path to handle spaces
            if [ -z "$backup_path" ]; then
                echo "Error: No backup path specified."
                exit 1
            fi
            # Use grep to filter processes by the backup path, using -- to handle options correctly
            PIDS=$(ps aux | grep '[m]ain.py' | grep -- "-b" | grep -- "-p $backup_path" | awk '{print $2}')
            if [ -n "$PIDS" ]; then
                echo "Stopping backup processes for path $backup_path..."
                for PID in $PIDS; do
                    echo "Killing PID $PID"
                    kill -15 "$PID"  # Attempt to stop gracefully with SIGTERM
                    sleep 1  # Give it a moment to terminate
                    if ps -p "$PID" > /dev/null; then
                        # echo "Process $PID did not terminate, killing forcefully..."
                        kill -9 "$PID"  # Forcefully stop with SIGKILL
                    fi
                done
            else
                echo "No backup processes found for $backup_path to stop."
            fi
            exit 0
            ;;
    esac
done

if [ "$#" -eq 0 ]; then
    # No arguments were passed, show help
    "$PYTHON_PATH" main.py -h
    exit 0
fi

# Use the found Python path to run the script
if $background_run_monitoring; then
    echo "Running in background."
    "$PYTHON_PATH" main.py "$@" &
else
    "$PYTHON_PATH" main.py "$@"
fi
