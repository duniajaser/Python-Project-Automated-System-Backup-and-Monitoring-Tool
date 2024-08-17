import os
import sys
import tarfile
from datetime import datetime

# Variables
BACKUP_PATH = sys.argv[1]  # Pass the backup directory path as an argument
LOG_FILE = os.path.expanduser("~/Desktop/python_project1/system_logs/system_monitor.log")

def create_directory_if_not_exists(directory):
    """Create a directory if it does not exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def backup_system(backup_path, log_file):
    """Perform the backup and log the process."""
    actual_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    day_of_week = datetime.now().strftime('%A')
    version = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_path, f'backup_{version}.tar.gz')

    # Ensure the backup directory exists
    create_directory_if_not_exists(os.path.dirname(log_file))
    create_directory_if_not_exists(backup_path)

    try:
        # Log the backup start time
        with open(log_file, 'a') as log:
            log.write(f"Backup starting at: {actual_start} on {day_of_week}\n")

        # Perform the backup
        with tarfile.open(backup_file, "w:gz") as tar:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    tar.add(file_path, arcname=os.path.relpath(file_path, backup_path))
        
        actual_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a') as log:
            log.write(f"Backup ended at: {actual_end} on {day_of_week}\n")
            log.write(f"{actual_start}, {actual_end}, {day_of_week} - Backup successful.\n")
            log.write("----------------------------------------------------\n")

    except Exception as e:
        actual_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a') as log:
            log.write(f"{actual_start}, {actual_end}, {day_of_week} - Backup encountered issues.\n")
            log.write("Error details: " + str(e) + '\n')
            log.write("----------------------------------------------------\n")
        sys.exit(1)

# Execute the backup
backup_system(BACKUP_PATH, LOG_FILE)
