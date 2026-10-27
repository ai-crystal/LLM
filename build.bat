@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PY="
where python >nul 2>nul
if not errorlevel 1 set "PY=python"
if not defined PY (
    where py >nul 2>nul
    if not errorlevel 1 set "PY=py -3"
)
if not defined PY (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
if not defined PY (
    echo [ERROR] Python 3 not found.
    pause
    exit /b 1
)

%PY% "book\build\build.py"
if errorlevel 1 (
    echo.
    echo Build failed. See book\build\work\book.log
    pause
    exit /b 1
)
echo.
echo Done. PDF is in output\llm-book.pdf
pause
