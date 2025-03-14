#!/bin/bash
cd /Users/manodhyaopallage/Refection/backend
# Try to use the virtual environment if it exists
if [ -d "venv" ]; then
  source venv/bin/activate
fi
python3 app.py
