@echo off
cd /d "%~dp0"
echo.
echo ===============================================
echo   Pushing to GitHub
echo   A login window will pop up - sign in there.
echo ===============================================
echo.
git push -u origin main
echo.
if %errorlevel%==0 (echo DONE - code is on GitHub now) else (echo FAILED - see message above)
echo.
pause