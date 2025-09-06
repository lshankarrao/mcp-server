@echo off
echo Starting MCP Weather App Demo
echo ===============================

echo.
echo Starting MCP Server...
start "MCP Server" cmd /k "cd server && python main.py"

echo Waiting for server to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting React Client...
start "React Client" cmd /k "cd client && npm run dev"

echo.
echo Demo started successfully!
echo.
echo Server: http://localhost:8000
echo Client: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop the demo...
pause > nul

echo.
echo Stopping demo...
taskkill /f /im "python.exe" 2>nul
taskkill /f /im "node.exe" 2>nul
echo Demo stopped.
pause
