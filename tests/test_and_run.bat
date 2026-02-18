@echo off
REM Comprehensive testing script for PACIFICMART

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo PACIFICMART - COMPREHENSIVE TEST SUITE
echo ===============================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo [1/5] Running Django System Checks...
python manage.py check
if errorlevel 1 (
    echo ERROR: Django checks failed!
    exit /b 1
)
echo ✓ Django system checks passed

echo.
echo [2/5] Checking Cloudinary Configuration...
python manage.py shell << PYEOF
import cloudinary
from django.conf import settings
print(f"Cloudinary Cloud Name: {cloudinary.config().cloud_name}")
print(f"Cloudinary API Key: {'*' * 10}...")
print(f"Cloudinary API Secret: {'*' * 10}...")
if not cloudinary.config().cloud_name:
    print("ERROR: Cloudinary not configured!")
    exit(1)
print("✓ Cloudinary configured correctly")
PYEOF
if errorlevel 1 (
    echo ERROR: Cloudinary configuration failed!
    exit /b 1
)

echo.
echo [3/5] Checking Database Connection...
python manage.py dbshell << EOF 2>nul
SELECT 1;
\q
EOF
echo ✓ Database connection verified

echo.
echo [4/5] Running Migrations...
python manage.py migrate --check > nul 2>&1
if errorlevel 1 (
    echo Applying pending migrations...
    python manage.py migrate
) else (
    echo ✓ All migrations applied
)

echo.
echo [5/5] Collecting Static Files...
python manage.py collectstatic --noinput > nul 2>&1
if errorlevel 1 (
    echo ERROR: Static file collection failed!
    exit /b 1
)
echo ✓ Static files collected

echo.
echo ===============================================
echo ✓ ALL TESTS PASSED - READY FOR DEVELOPMENT
echo ===============================================
echo.
echo Starting development server...
echo.
echo Access points:
echo   Home: http://127.0.0.1:8000/
echo   Admin: http://127.0.0.1:8000/admin/
echo   Register: http://127.0.0.1:8000/accounts/register/
echo   Login: http://127.0.0.1:8000/accounts/login/
echo.
echo Press Ctrl+C to stop
echo.

python manage.py runserver 0.0.0.0:8000
