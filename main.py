#!/usr/bin/env python3
from datetime import datetime, timedelta
import os
import sys
import argparse
import re
import subprocess
from crontab import CronTab

#--------------------------------------------------------------------------------------------------------------------------

def get_full_path(relative_path):
    """ Convert a relative path to a full path using the user's home directory. """
    home_dir = os.path.expanduser('~')
    return os.path.join(home_dir, relative_path)

# Define paths explicitly
LOG_FILE = get_full_path("Desktop/python_project1/system_logs/system_monitor.log")
PERFORMANCE_FILE=get_full_path("Desktop/python_project1/system_logs/system_performance.log")
MONITOR_SCRIPT=get_full_path("Desktop/python_project1/monitor_system.py")
REPORT_SCRIPT=get_full_path("Desktop/python_project1/generate_report.py")
BACKUP_SCRIPT=get_full_path("Desktop/python_project1/process_backup.py")

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

def schedule_cron_job(start_date, end_date, args):
    cron_command = f'python3 {MONITOR_SCRIPT} {args.start_monitoring}'
    
    # Set up the cron job to run every 3 minutes
    cron_entry = f"*/3 * * * * {cron_command}"
    
    if start_date:
        formatted_start_date = start_date.strftime('%Y%m%d%H%M')
        
        # Schedule the initial execution with 'at'
        subprocess.run(f'echo "{cron_command}" | at -t {formatted_start_date}', shell=True, stderr=subprocess.DEVNULL)
        print(f"Monitoring scheduled to start at {start_date.strftime('%Y-%m-%d %H:%M')}.")
        
        # Schedule the cron job to start right after the initial 'at' job
        at_time = start_date.strftime('%H:%M %m/%d/%Y')
        subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron_entry}") | crontab -', shell=True)
        print("Repeating monitoring every 3 minutes after initial start.")
    else:
        # Immediate start without a specific start date
        subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron_entry}") | crontab -', shell=True)
        print("Monitoring started immediately, repeating every 3 minutes.")

    if end_date:
        formatted_end_date = end_date.strftime('%Y%m%d%H%M')
        remove_command = f'crontab -l | grep -v "{cron_entry}" | crontab -'
        subprocess.run(f'echo "{remove_command}" | at -t {formatted_end_date}', shell=True, stderr=subprocess.DEVNULL)
        print(f"Monitoring scheduled to end at {end_date.strftime('%Y-%m-%d %H:%M')}.")

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

  #  print(f"Monitoring {date_message} with alerts to: {args.start_monitoring}")

    # Schedule the cron job
    schedule_cron_job(start_date, end_date, args)

    # periodic schdule
    schdule_periodic_report()

#--------------------------------------------------------------------------------------------------------------------------

def schdule_periodic_report():
    # Define the cron job command to run daily at 6 PM
    cron_command = f'0 18 * * * /usr/bin/python3 {REPORT_SCRIPT}'
    
    # Create a temporary file to store the new crontab
    temp_cron_file = '/tmp/temp_cron_file'
    try:
        # Get the current crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            current_crontab = result.stdout
        else:
            current_crontab = ""
        
        # Add the new cron job
        with open(temp_cron_file, 'w') as file:
            file.write(current_crontab)
            file.write(cron_command + '\n')
        
        # Install the new crontab
        subprocess.run(['crontab', temp_cron_file], check=True)
        # print(f"Cron job scheduled: {cron_command}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error scheduling cron job: {e}")
    finally:
        if os.path.exists(temp_cron_file):
            os.remove(temp_cron_file)

#--------------------------------------------------------------------------------------------------------------------------

def unschedule_backup(path):
    """Unschedule the backup for the given path."""
    validate_path(path)
    cron = CronTab(user=True)  # Load the current user's crontab
    job_marker = path

    # Iterate through cron jobs and remove those containing the job marker
    jobs_removed = 0
    for job in cron:
        if job_marker in job.command:
            cron.remove(job)
            jobs_removed += 1

    if jobs_removed > 0:
        cron.write()
        print(f"Removed {jobs_removed} scheduled backups for {path}.")
    else:
        print(f"No scheduled backup found for {path}.")

#--------------------------------------------------------------------------------------------------------------------------

def schedule_backup(args):
    """Schedule backup based on provided arguments, including date validations."""
    backup_path = args.p
    validate_path(backup_path)  # Ensure the backup path exists

    # Handle 'periodic' backup type
    if args.backup == 'periodic':
        if args.d:
            start_date = validate_date(args.d)
        else:
            start_date = datetime.now()  # Default to current time if no start date is provided
        
        if args.e:
            end_date = validate_date(args.e)
        else:
            end_date = None  # No end date
        
        if end_date and start_date >= end_date:
            print("Error: End date must be after the start date.")
            sys.exit(1)

        # Schedule periodic backup
        print(f"Scheduling {args.backup} backup every {args.t} hours at {backup_path}")
        if args.d:
            # If start date is provided, use 'at' to schedule cron job
            formatted_start_date = start_date.strftime('%Y%m%d%H%M')
            cron_command = f"*/{args.t} * * * * /usr/bin/python3 {BACKUP_SCRIPT} {backup_path}"
            at_time = start_date.strftime('%H:%M %m/%d/%Y')
            subprocess.run(f'echo "{cron_command}" | at -t {formatted_start_date}', shell=True, stderr=subprocess.DEVNULL)
            print(f"Backup scheduled to start at {args.d} and repeat every {args.t} hours.")
        else:
            # Immediate scheduling
            cron_command = f"*/{args.t} * * * * /usr/bin/python3 {BACKUP_SCRIPT} {backup_path}"
            subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -', shell=True)
            print(f"Backup started immediately, repeating every {args.t} hours.")
        
        if end_date:
            formatted_end_date = end_date.strftime('%Y%m%d%H%M')
            remove_command = f'crontab -l | grep -v "{cron_command}" | crontab -'
            subprocess.run(f'echo "{remove_command}" | at -t {formatted_end_date}', shell=True, stderr=subprocess.DEVNULL)
            print(f"Backup will end at {args.e}.")

    # Handle 'frequency' backup type
    elif args.backup == 'frequency':
        if not args.e or not args.t:
            print("Error: End date, and number of executions must be provided for frequency type backup.")
            sys.exit(1)

        start_date = validate_date(args.d)
        end_date = validate_date(args.e)
        if end_date <= start_date:
            print("Error: End date must be after the start date.")
            sys.exit(1)

        # Calculate the total duration in hours and the interval between each execution
        total_duration = (end_date - start_date).total_seconds() / 3600
        interval_minutes = max(1, int(total_duration * 60 / (args.t - 1)))  # Ensure at least 1 minute
        formatted_interval = format_time(interval_minutes)

        # Prepare the cron job command
        cron_command = f"*/{interval_minutes} * * * * /usr/bin/python3 {BACKUP_SCRIPT} {args.p}"

        if args.d:
            # Schedule the cron job to start at the start date using 'at'
            formatted_start_date = start_date.strftime('%Y%m%d%H%M')
            subprocess.run(f'echo "{cron_command}" | at -t {formatted_start_date} 2>/dev/null', shell=True, check=True)
            print(f"Backup scheduled to start at {args.d} and run every {formatted_interval}.")
        else:
            # Immediate scheduling
            subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -', shell=True)
            print(f"Backup started immediately, running every {formatted_interval}.")

        # Schedule the removal of the cron job at the end date
        end_at_time = end_date.strftime('%H:%M %m/%d/%Y')
        remove_command = f'crontab -l | grep -v "{cron_command}" | crontab -'
        subprocess.run(f'echo "{remove_command}" | at {end_at_time} 2>/dev/null', shell=True, check=True)
        print(f"Backup will end at {end_date}.")

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

    backup_filename = os.path.join(path, f"backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.tar.gz")
    backup_command = ['tar', '-czf', backup_filename, path]

    try:
        # Execute the backup command
        subprocess.run(backup_command, check=True)
        print(f"Backup successful: {backup_filename}")
    except subprocess.CalledProcessError as e:
        print(f"Backup failed: {e}")

#--------------------------------------------------------------------------------------------------------------------------

def stop_monitoring():
    """Stop system monitoring by removing the cron job associated with the monitor script."""
    # Access the current user's crontab
    cron = CronTab(user=True)
    jobs_removed = 0

    # Iterate through the jobs and remove those matching the monitoring script
    for job in cron:
        if MONITOR_SCRIPT in job.command:
            cron.remove(job)
            jobs_removed += 1
        if REPORT_SCRIPT in job.command:
            cron.remove(job)
            jobs_removed += 1


    # Write the changes back to the crontab
    if jobs_removed > 0:
        cron.write()
        print(f"Monitoring stopped. {jobs_removed} jobs removed.")
    else:
        print("No active monitoring job found.")

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
        unschedule_backup(args.unschedule)

    if getattr(args, 'backup_now', None):
        perform_backup(args.backup_now)

    if getattr(args, 'backup', None):
        schedule_backup(args)

    if getattr(args, 'stop_monitoring', False):
        stop_monitoring()

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
    parser.add_argument('-b', '--backup', type=str, choices=['periodic', 'frequency'], metavar='TYPE',
                        help=('Schedule a backup. Requires -p, -t, and optionally -d and -e.\n'
                              'Examples:\n'
                              '  -b periodic -t 6 -p /path/to/backup  # t represents hours between backups\n'
                              '  -b frequency -t 24 -p /path/to/backup -d "2024-01-01 12:00" -e "2024-01-02 12:00"'))
    parser.add_argument('-d', metavar='DATE', type=str, help='Start date and time in YYYY-MM-DD HH:MM format, required for frequency type.')
    parser.add_argument('-e', metavar='DATE', type=str, help='End date and time in YYYY-MM-DD HH:MM format, required for frequency type.')
    parser.add_argument('-t', metavar='TIMES_OR_HOURS', type=int, help='Specify the interval or frequency of backups: Number of hours or number of backups.')
    parser.add_argument('-p', metavar='PATH', type=str, help='Path where the directory for the backup process.')
    parser.add_argument('-u', '--unschedule', metavar='PATH', type=str, help='Unschedule a previously scheduled backup given the directory.')
    parser.add_argument('-s', '--start-monitoring', metavar='EMAIL', type=str,
                        help=('Start system monitoring with email alerts. Optional -d and -e for monitoring duration.\n'
                              'Example: -s user@example.com -d "2024-01-01 12:00" -e "2024-01-02 12:00"'))
    parser.add_argument('-k', '--stop-monitoring', action='store_true', help='Stop system monitoring and remove its process.')
    parser.add_argument('-l', '--logs', action='store_true', help='Display the contents of the system log file.')
    parser.add_argument('-r', '--report', action='store_true', help='Display a performance report from the system log.')
    parser.add_argument('-j', '--backup-now', metavar='PATH', type=str, help='Perform an immediate backup to the specified path.')

    return parser, parser.parse_args()

#--------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
