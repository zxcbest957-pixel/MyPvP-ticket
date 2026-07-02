@echo off
title Discord Ticket Bot
echo ===================================================
echo Discord Ticket Bot Setup and Launcher
echo ===================================================

:: Check if python is installed
set PYTHON_CMD=py
where py >nul 2>nul
if %errorlevel% neq 0 (
    set PYTHON_CMD=python
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not in PATH!
        pause
        exit /b
    )
)

:: Check for .env file
if not exist .env (
    echo [ERROR] .env file not found! Please create it.
    pause
    exit /b
)

:: Create virtual environment if it doesn't exist
if exist .venv goto :venv_exists
echo [INFO] Creating Python virtual environment venv...
%PYTHON_CMD% -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment!
    pause
    exit /b
)
:venv_exists

:: Install requirements
echo [INFO] Installing/updating packages from requirements.txt...
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements!
    pause
    exit /b
)

echo [INFO] Environment successfully configured.
echo Starting Discord Ticket Bot...
echo ---------------------------------------------------

.venv\Scripts\python.exe bot.py

pause
