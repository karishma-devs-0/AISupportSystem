@echo off
echo ========================================
echo Setting up Support Insight Platform
echo ========================================

REM Check Python
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    exit /b 1
)

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check for .env
if not exist .env (
    echo.
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env and add your OPENAI_API_KEY
    pause
)

REM Generate data
echo.
echo Generating synthetic data...
python generate_data.py

REM Run pipeline
echo.
echo Running AI pipeline...
python pipeline.py

echo.
echo ========================================
echo Setup complete!
echo.
echo To start: streamlit run app.py
echo ========================================
pause
