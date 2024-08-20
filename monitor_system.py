#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime
import subprocess
import psutil


# Get the current directory where the script is located
current_directory = os.path.dirname(os.path.abspath(__file__))

# Constants
CPU_THRESHOLD = 80
MEM_THRESHOLD = 90
DISK_THRESHOLD = 85

# Define log directory and file paths
LOG_DIR = os.path.join(current_directory, "system_logs")
LOG_FILE = os.path.join(LOG_DIR, "system_monitor.log")
CPU_ALERT_TIME_FILE = os.path.join(LOG_DIR, "cpu_alert_time.log")
MEM_ALERT_TIME_FILE = os.path.join(LOG_DIR, "mem_alert_time.log")
DISK_ALERT_TIME_FILE = os.path.join(LOG_DIR, "disk_alert_time.log")

# Get alert email from command-line arguments
ALERT_EMAIL = sys.argv[1] if len(sys.argv) > 1 else None

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Logging function
def log(message, type="Information"):
    # Adjust how the log line is formatted based on the type
    if type == "Warning":
        time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"{datetime.now().strftime('%H:%M:%S')} {type} - {time_stamp} : {message}\n"
    else:
        formatted_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {type} - {message}\n"
    
    with open(LOG_FILE, "a") as log_file:
        log_file.write(formatted_message)
        log_file.write("----------------------------------------------------\n")


# Function to send alerts
def send_alert_if_needed(last_alert_time_file, current_usage, alert_threshold, usage_type, email):
    current_time = int(time.time())
    try:
        with open(last_alert_time_file, "r") as file:
            last_alert_time = int(file.read().strip())
    except FileNotFoundError:
        last_alert_time = 0
    
    time_diff = current_time - last_alert_time

    if last_alert_time == 0 or time_diff > 1200:  # 20 minutes
        if current_usage > alert_threshold:
            alert_message = f"{usage_type} usage is above normal threshold at {current_usage}%"
            log(alert_message, type="Warning")
            send_email(email, f"High {usage_type} Usage Alert", alert_message)
            with open(last_alert_time_file, "w") as file:
                file.write(str(current_time))

# Function to send email
def send_email(to_address, subject, body):
    message = f"To: {to_address}\nFrom: d36831721@gmail.com\nSubject: {subject}\n\n{body}"
    
    # Open a process to send the email
    with subprocess.Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=subprocess.PIPE) as proc:
        proc.communicate(message.encode())

# Function to check system status
def check_system(email):
    # CPU Usage
    cpu_usage = psutil.cpu_percent(interval=1)
    if cpu_usage > CPU_THRESHOLD:
        send_alert_if_needed(CPU_ALERT_TIME_FILE, cpu_usage, CPU_THRESHOLD, "CPU", email)
    
    # Memory Usage
    memory_info = psutil.virtual_memory()
    mem_usage = memory_info.percent    
    if mem_usage > MEM_THRESHOLD:
        send_alert_if_needed(MEM_ALERT_TIME_FILE, mem_usage, MEM_THRESHOLD, "Memory", email)
    
    # Disk Usage
    disk_usage = psutil.disk_usage('/').percent
    if disk_usage > DISK_THRESHOLD:
        send_alert_if_needed(DISK_ALERT_TIME_FILE, disk_usage, DISK_THRESHOLD, "Disk", email)
    
    # Network Activity
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv

    # To calculate the rate, you need to monitor the change in bytes over time.
    time.sleep(1)  # wait a second to get the rate
    net_io_after = psutil.net_io_counters()
    rx_rate = (net_io_after.bytes_recv - bytes_recv) / 1024  # KB/s
    tx_rate = (net_io_after.bytes_sent - bytes_sent) / 1024  # KB/s

    # Log combined metrics
    log(f"CPU: {cpu_usage}% | Mem: {mem_usage}% | Disk: {disk_usage}% | Net: RX {rx_rate:.2f}KB/s, TX {tx_rate:.2f}KB/s")


if __name__ == "__main__":
    if not ALERT_EMAIL:
        print("Error: No email address provided.")
        print("Usage: <script> <email-address>")
        sys.exit(1)
    check_system(ALERT_EMAIL)
