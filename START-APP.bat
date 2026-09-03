@echo off
cd /d "%~dp0"
echo Starting app... browser will open shortly
python -m streamlit run app.py
pause
