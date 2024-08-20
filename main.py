#!/usr/bin/env python3
from datetime import datetime
import os
import sys
import argparse
import re
from apscheduler.schedulers.blocking import BlockingScheduler
from monitor_system import check_system
from generate_report import generate_report
from process_backup import backup_system

#--------------------------------------------------------------------------------------------------------------------------

def get_full_path(base_dir, relative_path):
    """ Convert a relative path to a full path using a base directory. """
    return os.path.join(base_dir, relative_path)

# Get the base directory dynamically
BASE_DIR = os.path.join(os.path.expanduser('~'), "Desktop/python_project1")

# Define paths using the base directory
LOG_FILE = get_full_path(BASE_DIR, "system_logs/system_monitor.log")
PERFORMANCE_FILE = get_full_path(BASE_DIR, "system_logs/system_performance.log")
MONITOR_SCRIPT = get_full_path(BASE_DIR, "monitor_system.py")
REPORT_SCRIPT = get_full_path(BASE_DIR, "generate_report.py")
BACKUP_SCRIPT = get_full_path(BASE_DIR, "process_backup.py")

#--------------------------------------------------------------------------------------------------------------------------

def validate_date(date_str):
    """Validate datetime format and ensure the date is not past. Default time to start of day if not provided."""
    try:
        # Attempt to parse the datetime with time
        date_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            # If initial parsing fails, assume only the date is provided and append "00:00" for start of the day
            date_time = datetime.strptime(date_str + " 00:00", "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Error: Invalid date format. Please use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'. Provided date: {date_str}")
            sys.exit(1)

    if date_time <= datetime.now():
        print(f"Error: The date '{date_str}' must be in the future.")
        sys.exit(1)
    return date_time

#--------------------------------------------------------------------------------------------------------------------------

def check_future_date(date_str):
    """Ensure the datetime is in the future."""
    date_time = validate_date(date_str)
    if date_time <= datetime.now():
        print(f"Error: The date '{date_str}' must be in the future.")
        sys.exit(1)
    return date_time

#--------------------------------------------------------------------------------------------------------------------------

def validate_email(email):
    """Validate email format."""
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print(f"Error: Invalid email format for {email}.")
        sys.exit(1)

#--------------------------------------------------------------------------------------------------------------------------

def display_logs():
    """Display the last 10 lines of the log file."""
    validate_path(LOG_FILE)  # Ensures the LOG_FILE path is valid
    print("Displaying Log Contents:")
    try:
        with open(LOG_FILE, 'r') as file:
            lines = file.readlines()
            print("".join(lines[-10:]))  # Print the last 10 lines
    except FileNotFoundError:
        print("Log file not found.")

#--------------------------------------------------------------------------------------------------------------------------

def generate_report():
    """Generate performance report from the log file."""
    validate_path(PERFORMANCE_FILE)  # Ensure the report script file exists
    print("Displaying Performance Report:")
    try:
        with open(PERFORMANCE_FILE, 'r') as file:
            print(file.read())
    except FileNotFoundError:
        print("Report script file not found.")

#--------------------------------------------------------------------------------------------------------------------------

def start_monitoring(args):
    """Start monitoring with email notifications."""
    validate_email(args.start_monitoring)
    
    start_date = check_future_date(args.d) if args.d else datetime.now()
    end_date = check_future_date(args.e) if args.e else None
    
    if end_date and start_date >= end_date:
        print("Error: End date must be after the start date.")
        sys.exit(1)

    # Construct the monitoring period message
    if start_date and end_date:
        date_message = f"from {start_date} to {end_date}"
    elif start_date:
        date_message = f"starting from {start_date} (no end date specified)"
    else:
        date_message = "with no specific start or end date"

    print(f"Monitoring {date_message} with alerts to: {args.start_monitoring}")
    scheduler = BlockingScheduler()
    
    #monitoring process every 3 minutes from start to end date and time
    scheduler.add_job(lambda: check_system(args.start_monitoring), 'interval', minutes=3, next_run_time=start_date, end_date=end_date)
    
    # reporting job to execute every day at 6:00 PM
    scheduler.add_job(generate_report, 'cron', hour=18, minute=0)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Monitoring interrupted by user.")
    finally:
        scheduler.shutdown()
        print("Monitoring stopped.")



#--------------------------------------------------------------------------------------------------------------------------

def unschedule_backup(path):
    """Unschedule the backup for the given path."""
    validate_path(path)
    

#--------------------------------------------------------------------------------------------------------------------------

def schedule_backup(args):
    """Schedule backup based on provided arguments, including date validations."""
    backup_path = args.p
    validate_path(backup_path)  # Ensure the backup path exists

    scheduler = BlockingScheduler()
    
    # Handle 'periodic' backup type
    if args.backup == 'periodic':
        if not args.t:
            print("Error: periodic hour number must be provided.")
            sys.exit(1)

        if args.d:
            start_date = validate_date(args.d)
        else:
            start_date = datetime.now()  # Default to current time if no start date is provided
        
        if args.e:
            end_date = validate_date(args.e)
        else:
            end_date = None  
        
        if end_date and start_date >= end_date:
            print("Error: End date must be after the start date.")
            sys.exit(1)

        # Schedule the backup with APScheduler
        scheduler.add_job(lambda: backup_system(backup_path, LOG_FILE), 'interval', hours=int(args.t), start_date=start_date, end_date=end_date)
        print(f"Backup scheduled to start at {start_date} and repeat every {args.t} hours.")
        if end_date:
            print(f"Backup will end at {end_date}.")

    # Handle 'frequency' backup type
    elif args.backup == 'frequency':
        if not args.e or not args.t:
            print("Error: End date, and number of executions must be provided for frequency type backup.")
            sys.exit(1)

        if args.d:
            start_date = validate_date(args.d)
        else:
            start_date = datetime.now()  # Default to current time if no start date is provided
        
        end_date = validate_date(args.e)
        if end_date <= start_date:
            print("Error: End date must be after the start date.")
            sys.exit(1)

        # Calculate the total duration in hours and the interval between each execution
        total_duration = (end_date - start_date).total_seconds() / 3600
        interval_minutes = max(1, int(total_duration * 60 / (args.t - 1)))  # Ensure at least 1 minute
        formatted_interval = format_time(interval_minutes)

        # Schedule the backup with APScheduler
        scheduler.add_job(lambda: backup_system(backup_path, LOG_FILE), 'interval', minutes=interval_minutes, start_date=start_date, end_date=end_date)
        print(f"Backup scheduled to run {args.t} times every {formatted_interval} from {start_date} to {end_date}.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Monitoring interrupted by user.")
    finally:
        scheduler.shutdown()
        print("Monitoring stopped.")



#--------------------------------------------------------------------------------------------------------------------------

def format_time(interval_minutes):
    """ Formats time from minutes to hours and minutes if more than one hour. """
    if interval_minutes >= 60:
        hours = interval_minutes // 60
        minutes = interval_minutes % 60
        if minutes > 0:
            return f"{hours} hours and {minutes} minutes"
        else:
            return f"{hours} hours"
    return f"{interval_minutes} minutes"

#--------------------------------------------------------------------------------------------------------------------------

def perform_backup(path):
    """Perform immediate backup to the specified path."""
    validate_path(path)  
    print(f"Performing immediate backup at: {path}")
    backup_system(path, LOG_FILE)

#--------------------------------------------------------------------------------------------------------------------------

def main():
    parser, args = help_maker()
    if len(sys.argv) == 1:  # No arguments provided
        parser.print_help()
        sys.exit(1)

    # Validate path if any operation that requires a path is requested
    if any(getattr(args, opt, None) for opt in ['p', 'u', 'j', 'b']):
        if hasattr(args, 'p') and args.p:
            validate_path(args.p)  # This will exit if the path does not exist
        else:
            print("No path provided for required operation.")
            sys.exit(1)
    

    # Handle each operation that requires a path validation within its own context
    if getattr(args, 'logs', False):
        display_logs()

    if getattr(args, 'report', False):
        generate_report()

    if getattr(args, 'unschedule', None):
        """the unscheduling   operation is already stopped from the run.sh script."""

    if getattr(args, 'backup_now', None):
        perform_backup(args.backup_now)

    if getattr(args, 'backup', None):
        schedule_backup(args)

    if getattr(args, 'stop_monitoring', False):
        """the system monitoring reporting operation is already stopped from the run.sh script."""

    if getattr(args, 'start_monitoring', None):
        start_monitoring(args)

    sys.exit(0)

#--------------------------------------------------------------------------------------------------------------------------

def validate_path(path):
    """Check if the specified path exists."""
    #print(f"Checking if path exists: {path}")
    if not os.path.exists(path):
        print(f"Error: The specified path '{path}' does not exist.")
        sys.exit(1)

#--------------------------------------------------------------------------------------------------------------------------

def help_maker():
    parser = argparse.ArgumentParser(
        description="Automated Backup System and Monitoring Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-b', '--backup', type=str, choices=['periodic', 'frequency'], metavar='<TYPE>', 
                        help=('Schedule a backup. Requires -p, -t, and optionally -d and -e.\n'
                              'Examples:\n'
                              '  -b periodic -t 6 -p /path/to/backup  # t represents hours between backups\n'
                              '  -b frequency -t 24 -p /path/to/backup -d "2024-01-01 12:00" -e "2024-01-02 12:00"'))
    parser.add_argument('-d', metavar='<DATE>', type=str, help='Start date and time in YYYY-MM-DD HH:MM format, required for frequency type.')
    parser.add_argument('-e', metavar='<DATE>', type=str, help='End date and time in YYYY-MM-DD HH:MM format, required for frequency type.')
    parser.add_argument('-t', metavar='<TIMES_OR_HOURS>', type=int, help='Specify the interval or frequency of backups: Number of hours or number of backups.')
    parser.add_argument('-p', metavar='<PATH>', type=str, help='Path where the directory for the backup process.')
    parser.add_argument('-u', '--unschedule', metavar='<PATH>', type=str, help='Unschedule a previously scheduled backup given the directory.')
    parser.add_argument('-s', '--start-monitoring', metavar='<EMAIL>', type=str,
                        help=('Start system monitoring with email alerts. Optional -d and -e for monitoring duration.\n'
                              'Example: -s user@example.com -d "2024-01-01 12:00" -e "2024-01-02 12:00"'))
    parser.add_argument('-k', '--stop-monitoring', action='store_true', help='Stop system monitoring and remove its process.')
    parser.add_argument('-l', '--logs', action='store_true', help='Display the contents of the system log file.')
    parser.add_argument('-r', '--report', action='store_true', help='Display a performance report from the system log.')
    parser.add_argument('-j', '--backup-now', metavar='<PATH>', type=str, help='Perform an immediate backup to the specified path.')

    return parser, parser.parse_args()

#--------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
