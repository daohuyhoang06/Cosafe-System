@echo off
echo Starting Cosafe System...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker first.
    exit /b 1
)

REM Start Elasticsearch
echo Starting Elasticsearch...
docker-compose up -d

REM Wait for Elasticsearch
echo Waiting for Elasticsearch to be ready...
:wait_loop
timeout /t 2 /nobreak >nul
curl -s http://localhost:9200/_cluster/health | find "status" >nul
if errorlevel 1 goto wait_loop

echo Elasticsearch is ready!

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    py -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install backend dependencies
echo Installing backend dependencies...
py -m pip install --upgrade pip
py -m pip install -r requirements.txt

REM Start backend in background
echo Starting backend server...
start "Cosafe Backend" cmd /k "venv\Scripts\activate.bat && py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Start frontend
echo Starting frontend server...
cd frontend
start "Cosafe Frontend" cmd /k "npm run dev"
cd ..

echo.
echo Cosafe System is running!
echo.
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
echo Press any key to stop all services...
pause >nul

REM Stop services
echo Stopping services...
docker-compose down
taskkill /FI "WindowTitle eq Cosafe Backend*" /F
taskkill /FI "WindowTitle eq Cosafe Frontend*" /F
