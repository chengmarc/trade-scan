@echo off

echo Starting virtual environment setup.
echo.
python -m venv __venv__
call __venv__\Scripts\activate.bat
pip install dependencies\dist\tsl-dependencies-1.0.tar.gz
echo.
echo Virtual environment setup completed.
pause

echo.
echo ##########################
echo ##### Extract for US #####
echo ##########################
echo.
call core-process\trade_scan_stock_us.py

echo.
echo ##############################
echo ##### Extract for Canada #####
echo ##############################
echo.
call core-process\trade_scan_stock_ca.py

echo.
echo #################################
echo ##### Extract for Hong Kong #####
echo #################################
echo.
call core-process\trade_scan_stock_us.py

echo.
echo #############################
echo ##### Extract for China #####
echo #############################
echo.
call core-process\trade_scan_stock_us.py

echo.
echo Execution fully completed.
pause