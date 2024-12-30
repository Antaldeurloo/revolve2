@echo off

REM Example: Running the Python script with different parameters
powershell -ExecutionPolicy Bypass -Command "Set-Location 'D:\antal\thesis_project\.venv\Scripts'; .\Activate.ps1; python 'D:\antal\thesis_project\.venv\revolve2\examples\robot_bodybrain_ea_database\main.py' GRN evolution testo1.sqlite False False False