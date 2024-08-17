# Python-Project-Automated-System-Backup-and-Monitoring-Tool

This repository contains a suite of tools developed in Python for automating system backups and monitoring system performance. It includes scripts for handling backups, monitoring system resources, and generating alerts when certain thresholds are exceeded.

## Project Structure

- `main.py`: Central script that orchestrates backup and monitoring functionalities.
- `monitor_system.py`: Script for monitoring system metrics such as CPU, memory, disk usage, and network activity.
- `process_backup.py`: Manages the creation of backups, including compression and versioning.
- `generate_report.py`: Generates reports based on system logs and monitoring data.
- `run.sh`: Shell script to run the main Python script, ensuring the right Python interpreter is used.

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

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/duniajaser/Python-Project-Automated-System-Backup-and-Monitoring-Tool.git
cd Python-Project-Automated-System-Backup-and-Monitoring-Tool
