#!/bin/bash

echo "This script will show you how to set up a cron job to run the AI Employee every 5 minutes."
echo

# Get the absolute path to the project directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
SCRIPT_PATH="$PROJECT_ROOT/scripts/run_ai_employee.py"
PYTHON_PATH=$(which python) # Or specify your python path directly

if [ -z "$PYTHON_PATH" ]; then
    echo "Error: Python executable not found. Please ensure python is in your PATH."
    exit 1
fi

CRON_JOB="*/5 * * * * $PYTHON_PATH $SCRIPT_PATH"

echo "==================================="
echo "  Cron Job Setup Instructions"
echo "==================================="
echo
echo "1. Open your crontab for editing by running:"
echo "   crontab -e"
echo
echo "2. Add the following line to the file:"
echo
echo "   $CRON_JOB"
echo
echo "3. Save and close the file. The cron job is now active."
echo
echo "==================================="