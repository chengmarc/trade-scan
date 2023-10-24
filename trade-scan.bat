@echo off
echo Starting virtual environment setup.
echo.
python -m venv __venv__
call __venv__\Scripts\activate.bat
pip install dependencies\dist\tsl-dependencies-1.1.tar.gz
echo.
echo Virtual environment setup completed.
call core-process\trade_scan_gui.py