@echo off
REM ============================================================
REM  git-pull.bat  —  Pull latest changes from GitHub (origin/main)
REM  Usage: double-click OR run from terminal:  git-pull.bat
REM ============================================================
title Git Pull
echo.
echo ============================================
echo   GIT PULL - Latest data laa raha hoon...
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] Remote se fetch + pull:
git pull origin main
if errorlevel 1 (
    echo.
    echo [ERROR] Pull fail ho gaya. Internet / remote check karo.
    pause
    exit /b 1
)

echo.
echo [2/2] Current status:
git status

echo.
echo ============================================
echo   DONE! Aapka repo ab latest hai.
echo ============================================
echo.
pause
