@echo off

setlocal
set PYTHON=python
set PYTHONPATH=%PYTHONPATH%;%~dp0\compiler
set PYTHONIOENCODING="utf-8"
"%PYTHON%" "%~dp0\main.py" --print-trees %~1 > "%~dpn1.ll"
endlocal