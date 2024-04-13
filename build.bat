echo off
cls
rmdir /s /q dist
rmdir /s /q build
pyinstaller -F textAdventure.py
rmdir /s /q build
del /s /q textAdventure.spec