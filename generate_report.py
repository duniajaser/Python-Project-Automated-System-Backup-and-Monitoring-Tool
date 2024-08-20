import os
from datetime import datetime

# Define the log file paths
LOG_FILE = os.path.expanduser("~/Desktop/python_project1/system_logs/system_performance.log")
LOG_FILE_MONITOR = os.path.expanduser("~/Desktop/python_project1/system_logs/system_monitor.log")

def create_log_file_silently(file_path):
    """Create a log file if it does not exist, silently."""
    if not os.path.isfile(file_path):
        try:
            with open(file_path, 'a'):
                pass
        except Exception as e:
            print(f"Error creating log file {file_path}: {e}")

def parse_line(line):
    """Extract performance metrics from a log line."""
    try:
        parts = line.split('|')
        if len(parts) >= 4:
            cpu_usage = float(parts[0].split('CPU:')[1].split('%')[0].strip())
            mem_usage = float(parts[1].split('Mem:')[1].split('%')[0].strip())
            disk_usage = float(parts[2].split('Disk:')[1].split('%')[0].strip())
            net_rx = float(parts[3].split('RX')[1].split('KB')[0].strip())
            net_tx = float(parts[3].split('TX')[1].split('KB')[0].strip())
            return cpu_usage, mem_usage, disk_usage, net_rx, net_tx
        else:
            print(f"Unexpected format in line: {line}")
            return None, None, None, None, None
    except (IndexError, ValueError) as e:
        print(f"Error parsing line: {line}. Error: {e}")
        return None, None, None, None, None

def generate_report():
    """Generate a performance report based on log files."""
    # Initialize sum and count variables
    total_cpu_usage = 0
    total_mem_usage = 0
    total_disk_usage = 0
    total_rx = 0
    total_tx = 0
    count = 0
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Read log file lines
    try:
        with open(LOG_FILE_MONITOR, 'r') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error reading log file {LOG_FILE_MONITOR}: {e}")
        return

    # Extract and compute the necessary data
    for line in lines:
        if "Information" in line:
            cpu_usage, mem_usage, disk_usage, net_rx, net_tx = parse_line(line)
            if cpu_usage is not None:
                count += 1
                total_cpu_usage += cpu_usage
                total_mem_usage += mem_usage
                total_disk_usage += disk_usage
                total_rx += net_rx
                total_tx += net_tx

    # Calculate averages
    if count > 0:
        average_cpu_usage = total_cpu_usage / count
        average_mem_usage = total_mem_usage / count
        average_disk_usage = total_disk_usage / count
        average_rx = total_rx / count
        average_tx = total_tx / count
    else:
        average_cpu_usage = average_mem_usage = average_disk_usage = average_rx = average_tx = 0

    # Write the performance report to the log file
    try:
        with open(LOG_FILE, 'w') as file:
            file.write("================================================\n")
            file.write(f"System Performance Report for {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...\n")
            file.write("------------------------------------------------\n\n")
            file.write("Summary of System Performance:\n")
            file.write(f" - Average CPU Usage: {average_cpu_usage:.2f}%\n")
            file.write(f" - Average Memory Usage: {average_mem_usage:.2f}%\n")
            file.write(f" - Average Disk Usage: {average_disk_usage:.2f}%\n")
            file.write(f" - Average RX Rate: {average_rx:.2f} KB/s\n")
            file.write(f" - Average TX Rate: {average_tx:.2f} KB/s\n\n")

            # Summarize backups for today
            successful_count = sum(1 for line in lines if "Backup successful" in line and today_date in line)
            issues_count = sum(1 for line in lines if "Backup encountered issues" in line and today_date in line)
            file.write(f"Backup Summary for {today_date}:\n")
            file.write(f" - Successful Backups: {successful_count}\n")
            file.write(f" - Backups with Issues: {issues_count}\n\n")

            # Warning Summary
            warning_count = sum(1 for line in lines if today_date in line and "Warning:" in line)
            if warning_count > 0:
                file.write(f"Warnings for {today_date}:\n")
                file.write(f" - Number of Warnings: {warning_count}\n")
            else:
                file.write("No warning data available for today.\n")
            file.write("\n================================================\n")
    except Exception as e:
        print(f"Error writing report to log file {LOG_FILE}: {e}")

# Create or verify log files silently
create_log_file_silently(LOG_FILE)
create_log_file_silently(LOG_FILE_MONITOR)
