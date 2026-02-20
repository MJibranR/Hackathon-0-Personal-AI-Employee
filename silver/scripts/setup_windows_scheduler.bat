@echo off
echo This script will set up a Windows Scheduled Task to run the AI Employee every 5 minutes.
echo.

set "PYTHON_EXE_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe"
REM Assumes project root is parent of scripts directory
set "PROJECT_ROOT=%~dp0.."
set "SCRIPT_PATH=%PROJECT_ROOT%\scripts\run_ai_employee.py"
set "TASK_NAME=AIEmployeePlanner"

echo ===================================
echo  Windows Scheduled Task Setup
echo ===================================
echo.
echo Task Name: %TASK_NAME%
echo Script: %SCRIPT_PATH%
echo Frequency: Every 5 minutes
echo.
echo Please ensure the Python path is correct:
echo %PYTHON_EXE_PATH%
echo If not, please edit this script.
echo.
pause

schtasks /create /sc minute /mo 5 /tn "%TASK_NAME%" /tr "\"%PYTHON_EXE_PATH%\" \"%SCRIPT_PATH%\"" /f

echo.
echo Verifying task...
schtasks /query /tn "%TASK_NAME%"

echo.
echo ===================================
echo  Setup Complete!
echo ===================================
echo The task '%TASK_NAME%' has been created.
echo.
pause
