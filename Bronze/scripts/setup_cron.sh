#!/bin/bash

# This script sets up a cron job to run run_ai_employee.py as a daemon.

# Ensure the script is executable
chmod +x scripts/run_ai_employee.py

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Define the path to the Python interpreter
PYTHON_PATH="$(which python)"
if [ -z "$PYTHON_PATH" ]; then
    echo "Error: Python interpreter not found. Please ensure Python is installed and in your PATH."
    exit 1
fi

# Define the path to the AI employee script
AI_EMPLOYEE_SCRIPT="$PROJECT_DIR/scripts/run_ai_employee.py"

# Define the cron job command
CRON_COMMAND="$PYTHON_PATH $AI_EMPLOYEE_SCRIPT"

# Add the cron job
(crontab -l 2>/dev/null; echo "@reboot sleep 30 && $CRON_COMMAND > $PROJECT_DIR/logs/run_ai_employee.log 2>&1 &") | crontab -
echo "Cron job added to run AI employee script on reboot:"
echo "@reboot sleep 30 && $CRON_COMMAND > $PROJECT_DIR/logs/run_ai_employee.log 2>&1 &"
echo "To view your cron jobs, run: crontab -l"
echo "To remove the cron job, run: crontab -e and delete the line."
