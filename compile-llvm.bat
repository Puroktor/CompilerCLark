@echo off

if "%~1"=="" (
  (
    echo Usage:
    echo   %~nx0 src
  ) 1>&2
  exit 1
)
if not exist "%~1" (
  (
    echo File "%~1" not exists
  ) 1>&2
  exit 2
)

del /f /q "%~dpn1.exe" "%~dpn1.ll"
call "%~dp0\run.bat" %~1
set STATUS=%ERRORLEVEL%
if not "%STATUS%"=="0" (
  del /f /q "%~dpn1.ll"
  exit %STATUS%
)
call clang "%~dpn1.ll" -o "%~dpn1.exe"