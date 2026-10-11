@echo off
title StudyAI
cd /d C:\Users\HP\Documents\studyIA
start "" cmd /c "timeout /t 4 /nobreak >nul && start http://127.0.0.1:5000"
.venv\Scripts\python.exe app.py
pause