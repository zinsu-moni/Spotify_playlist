@echo off
echo Installing Spotify Billboard Hot 100 Playlist Generator requirements...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Error installing requirements. Please make sure Python is installed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Requirements installed successfully!
echo.
echo Now you need to:
echo 1. Update the .env file with your Spotify credentials
echo 2. Run the application with: python app.py
echo.
echo Press any key to exit...
pause
