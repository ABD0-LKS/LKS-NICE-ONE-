#!/bin/bash

echo "Starting POS System..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.7+ and try again."
    exit 1
fi

# Check if PyQt5 is installed
python3 -c "import PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "PyQt5 is not installed. Installing now..."
    pip3 install PyQt5==5.15.9
    if [ $? -ne 0 ]; then
        echo "Failed to install PyQt5"
        exit 1
    fi
fi

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Run the POS system
python3 run_pos.py

if [ $? -ne 0 ]; then
    echo
    echo "Application encountered an error"
    read -p "Press Enter to continue..."
fi
