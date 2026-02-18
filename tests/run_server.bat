@echo off
REM Run development server with activated virtual environment

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting Django development server...
echo.
echo Access the site at: http://127.0.0.1:8000
echo Admin at: http://127.0.0.1:8000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver 0.0.0.0:8000

pause
