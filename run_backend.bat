@echo off
echo Starting EduVerify Backend Server...
cd /d "%~dp0backend"
call ..\.venv\Scripts\activate.bat
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
