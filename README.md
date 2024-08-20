# Python-Project-Automated-System-Backup-and-Monitoring-Tool

This repository contains a suite of tools developed in Python for automating system backups and monitoring system performance. It includes scripts for handling backups, monitoring system resources, and generating alerts when certain thresholds are exceeded.

## Project Structure

- `run.sh`: A shell script to manage the execution of Python scripts for system monitoring and backups. It includes options for starting, stopping, and managing processes in the background.
- `process_backup.py`: Python script for automating system backups with options for scheduling and managing backup frequency.
- `monitor_system.py`: Python script to monitor system performance, capable of running as a background service.
- `main.py`: Main entry point for the system tools, interfacing with other scripts and handling command-line arguments for system monitoring and backups.
- `generate_report.py`: Script for generating reports based on system performance data collected by `monitor_system.py`.

## Features

1. **Automated Backup System**
   - Backs up specified directories and files.
   - Creates compressed archives of the backups.
   - Implements versioning for backups.
   - Schedules backups using cron jobs.

2. **System Performance Monitoring**
   - Monitors CPU, memory, disk, and network activity.
   - Generates alerts when usage exceeds predefined thresholds.
   - Logs system performance data.
   - Automatically generates and updates reports on system performance.

3. **User Interface**
   - Provides a command-line interface for easy configuration and control.
   - Allows users to view logs and generated reports.
   - Includes help features to guide users on how to use the tool.

