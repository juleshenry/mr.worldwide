#!/bin/bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Virtual environment set up successfully!"
echo "To use it, run: source venv/bin/activate"
