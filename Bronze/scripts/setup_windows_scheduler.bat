@echo off
REM This script sets up a Windows Task Scheduler job to run run_ai_employee.py as a daemon.

REM Get the absolute path to the project directory
SET "PROJECT_DIR=%~dp0.."
FOR %%i IN ("%PROJECT_DIR%") DO SET "PROJECT_DIR=%%~fi"

REM Define the path to the Python interpreter
REM Try to find Python in common locations
WHERE python.exe >NUL 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Python interpreter not found. Please ensure Python is installed and in your PATH.
    GOTO :EOF
)
SET "PYTHON_EXE=python.exe"

REM Define the path to the AI employee script
SET "AI_EMPLOYEE_SCRIPT=%PROJECT_DIR%\scripts\run_ai_employee.py"

REM Define the log file path
SET "LOG_FILE=%PROJECT_DIR%\logs\run_ai_employee.log"

REM Create the Task Scheduler job
REM The task will run at system startup and repeat indefinitely.
SCHTASKS /Create /TN "AI Employee Daemon" /TR "%PYTHON_EXE% %AI_EMPLOYEE_SCRIPT% > \"%LOG_FILE%\" 2>&1" /SC ONSTART /RU SYSTEM /RL HIGHEST /Z /F
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Failed to create Task Scheduler job.
    GOTO :EOF
)

ECHO Task Scheduler job "AI Employee Daemon" created successfully.
ECHO The task is configured to run "%PYTHON_EXE% %AI_EMPLOYEE_SCRIPT%" at system startup.
ECHO Output will be redirected to "%LOG_FILE%".
ECHO To view the task, open Task Scheduler (taskschd.msc).
ECHO To delete the task, run: SCHTASKS /Delete /TN "AI Employee Daemon" /F
