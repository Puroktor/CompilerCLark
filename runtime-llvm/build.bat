@echo off

%~d0
cd "%~dp0"

del /f /q .\runtime.ll
call clang -S runtime.c -emit-llvm