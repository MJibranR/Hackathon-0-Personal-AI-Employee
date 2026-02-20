@echo off
REM This script runs all the necessary components for the AI Employee.

echo Starting AI Employee...
echo Make sure you have created a .env file with your credentials.

REM Start the watchers and processors in the background
start "File Watcher" cmd /c "python watcher.py"
start "Gmail Watcher" cmd /c "python skills\gmail_watcher.py"
start "Planner" cmd /c "python scripts\planner.py"
start "Processor" cmd /c "python scripts\processor.py"
start "Executor" cmd /c "python scripts\executor.py"

echo.
echo All components are starting up in separate windows.
echo You can monitor the logs in the 'logs' directory.
echo To stop the AI Employee, close all the new command prompt windows.
echo.
pause
