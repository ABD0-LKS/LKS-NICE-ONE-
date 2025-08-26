#!/usr/bin/env python3
"""
Store Manager POS System Launcher
Simple launcher script for the POS system
"""

import sys
import os

def main():
    print("Starting Store Manager POS System...")
    
    try:
        # Import and run the main application
        from main import main as run_main
        run_main()
        
    except ImportError as e:
        print(f"Error importing main application: {e}")
        print("Make sure all required files are present.")
        input("Press Enter to exit...")
        return 1
        
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
