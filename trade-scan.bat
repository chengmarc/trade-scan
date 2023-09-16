@echo off

if not exist "market-data\us-market" mkdir market-data\us-market
if not exist "market-data\ca-market" mkdir market-data\ca-market
if not exist "market-data\zh-market" mkdir market-data\zh-market
if not exist "market-data\hk-market" mkdir market-data\hk-market

echo Starting virtual environment setup.
echo.
python -m venv __venv__
call __venv__\Scripts\activate.bat
pip install dependencies\dist\tsl-dependencies-1.0.tar.gz
echo.
echo Virtual environment setup completed.
pause

call core-process\trade_scan_main.py
pause