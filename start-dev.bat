@echo off
echo Starting AI Role-Playing Website Development Environment...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo Installing Python dependencies...
cd /d "%~dp0api"
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python packages...
pip install -r requirements.txt

echo.
echo Installing Node.js dependencies...
cd /d "%~dp0"
npm install

echo.
echo Starting backend server...
cd /d "%~dp0api"
start "Backend Server" cmd /k "venv\Scripts\activate.bat && python main.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting frontend development server...
cd /d "%~dp0"
start "Frontend Server" cmd /k "npm run dev"

echo.
echo Development servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit...
pause >nul