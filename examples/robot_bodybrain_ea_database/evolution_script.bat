@echo off

REM Activate the virtual environment
call "D:\antal\thesis_project\.venv\Scripts\activate.ps1"

python "D:\antal\thesis_project\.venv\revolve2\examples\robot_bodybrain_ea_database\main.py" GRN evolution testo1.sqlite False False False
python "D:\antal\thesis_project\.venv\revolve2\examples\robot_bodybrain_ea_database\main.py" GRN_system evolution testo2.sqlite False False False
python "D:\antal\thesis_project\.venv\revolve2\examples\robot_bodybrain_ea_database\main.py" GRN_system_adv evolution testo3.sqlite False False False