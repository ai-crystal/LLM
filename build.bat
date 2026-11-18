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

rem ---- usage ----
rem   build.bat                 build every book
rem   build.bat v2-basics       build one book
rem   build.bat check           health check only
rem   build.bat site            regenerate sidebar / per-book README
rem   build.bat figures         redraw all figures
rem   build.bat figures 03      redraw figures of chapter 03 (volume 2 only)

if "%~1"=="" goto build_all
if /i "%~1"=="check" goto check
if /i "%~1"=="site" goto site
if /i "%~1"=="figures" goto figures
goto build_one

:build_all
%PY% "books/build/build.py"
if errorlevel 1 goto failed
echo.
echo Done. All PDFs are in output\
pause
exit /b 0

:build_one
%PY% "books/build/build.py" --book %1
if errorlevel 1 goto failed
echo.
echo Done. output\
pause
exit /b 0

:site
%PY% "books/build/make_site.py"
if errorlevel 1 goto failed
echo.
echo Site navigation regenerated.
pause
exit /b 0

:check
%PY% "books/build/build.py" --check
pause
exit /b 0

:figures
if "%~2"=="" (
    %PY% "books/code/figs_v1.py"
    if errorlevel 1 goto failed
    %PY% "books/code/figs_v2.py"
) else (
    %PY% "books/code/figs_v2.py" %2
)
if errorlevel 1 goto failed
echo.
echo Figures redrawn.
pause
exit /b 0

:failed
echo.
echo [FAILED] see the log under books/build/work/
pause
exit /b 1
