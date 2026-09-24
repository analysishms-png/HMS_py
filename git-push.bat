@echo off
REM ============================================================
REM  git-push.bat  —  Add + Commit + Push to GitHub (origin/main)
REM  Usage: double-click OR run from terminal:  git-push.bat
REM         Commit message aapko poochha jayega.
REM ============================================================
title Git Push
setlocal

cd /d "%~dp0"

echo.
echo ============================================
echo   GIT PUSH - Changes GitHub par bhej rahe hain
echo ============================================
echo.

echo [1/4] Changed files:
git status --short
echo.

if "%~1"=="" (
    set /p COMMIT_MSG=Commit message likho (e.g. "Fixed billing bug": 
) else (
    set "COMMIT_MSG=%~1"
)

if "%COMMIT_MSG%"=="" (
    echo [ERROR] Commit message khali hai! Kuch likho.
    pause
    exit /b 1
)

echo.
echo [2/4] Sab files add kar rahe hoon:
git add -A
if errorlevel 1 (
    echo [ERROR] Add fail.
    pause
    exit /b 1
)

echo.
echo [3/4] Commit kar rahe hoon:
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo.
    echo [INFO] Commit nahi hua - shayad koi naya change nahi hai.
    git status
    pause
    exit /b 0
)

echo.
echo [4/4] Push kar rahe hoon:
git push origin main
if errorlevel 1 (
    echo.
    echo [ERROR] Push fail. Pehle "git-pull.bat" chalao, phir dobara try karo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   DONE! Sab kuch GitHub par push ho gaya.
echo ============================================
echo.
pause
endlocal
