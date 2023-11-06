@echo off
python --version
echo Starting virtual environment setup.
echo.
python -m venv __venv__
call __venv__\Scripts\activate.bat
pip install dependencies\dist\tsl-dependencies-1.2.tar.gz
echo.
echo Virtual environment setup completed.
echo.
call core-process\trade_scan_gui.py