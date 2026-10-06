#!/usr/bin/env bash
# One-click setup and run for macOS / Linux
set -e
cd "$(dirname "$0")"
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
[ -f data/raw/Fake.csv ] || python gen_dataset.py
[ -f data/processed/news_clean.csv ] || python prepare_data.py
[ -f model/model.pkl ] || python train.py
python app.py
