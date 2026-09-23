@echo off
title CircuitHealth AI Backend Server
cd /d "C:\Users\mrush\CircuitHealthAI\laptop_backend"
call venv\Scripts\activate.bat

echo Starting Uvicorn Server in background...
start /b uvicorn server:app --reload

echo Waiting 3 seconds for server startup...
timeout /t 3 /nobreak >nul

echo Running Test Client...
python test_client.py
pause