# PowerShell script to run development server with activated virtual environment

Write-Host "Activating virtual environment..."
& ".\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Starting Django development server..." -ForegroundColor Green
Write-Host ""
Write-Host "Access the site at: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Admin at: http://127.0.0.1:8000/admin" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver 0.0.0.0:8000

Read-Host "Press Enter to exit"
