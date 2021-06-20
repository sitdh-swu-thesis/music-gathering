#!/bin/sh

if [ ! -d "venv" ]; then
    echo "Virtual env folder does not exists, creating"
    virtualenv -p python3 venv
fi

source venv/bin/activate
pip install pip --upgrade

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi