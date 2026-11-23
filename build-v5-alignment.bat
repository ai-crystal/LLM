@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

rem ---- locate Python 3 ----
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
    echo [ERROR] Python 3 not found. Install it from https://www.python.org/
    pause
    exit /b 1
)

rem ---- install missing packages on first run ----
%PY% -c "import PIL, pymupdf" >nul 2>nul
if errorlevel 1 (
    echo [setup] installing pillow and pymupdf ...
    %PY% -m pip install --quiet pillow pymupdf
)

%PY% -c "import matplotlib, fontTools" >nul 2>nul
if errorlevel 1 (
    echo [setup] installing matplotlib and fonttools ...
    %PY% -m pip install --quiet matplotlib fonttools
)

rem ---- build one book: v5-alignment ----
echo [build] v5-alignment
%PY% "books/build/build.py" --book v5-alignment
if errorlevel 1 (
    echo.
    echo [FAILED] see books/build/work/v5-alignment/book-v5-alignment.log
    pause
    exit /b 1
)
echo.
echo Done. output/v5-alignment.pdf
pause
