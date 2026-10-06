@echo off
REM One-click setup and run for Windows
cd /d "%~dp0"
if not exist venv python -m venv venv
call venv\Scripts\activate
pip install -q -r requirements.txt
if not exist data\raw\Fake.csv python gen_dataset.py
if not exist data\processed\news_clean.csv python prepare_data.py
if not exist model\model.pkl python train.py
python app.py
pause
