@echo off
echo Installing required Python libraries...

:: Optional: Create and activate virtual environment
:: python -m venv venv
:: call venv\Scripts\activate

:: Upgrade pip
python -m pip install --upgrade pip

:: Install required packages
pip install Pillow
pip install requests
pip install tkcalendar
pip install pyserial

echo.
echo Installation complete.
pause
