@echo off

echo Starting virtual environment setup.
echo.
python -m venv __venv__
call __venv__\Scripts\activate.bat
pip install dependencies\dist\tsl-dependencies-1.0.tar.gz
echo.
echo Virtual environment setup completed.
pause

call core-process\trade_scan_crypto.py
echo.
echo Execution fully completed.
pause