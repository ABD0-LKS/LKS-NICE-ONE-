#!/usr/bin/env python3
"""
Store Manager POS System
Professional Point of Sale Application

Run this script to start the POS system.
Make sure to configure MySQL connection settings first if this is your first time.
"""

import sys
import os
import subprocess

def check_requirements():
    """Check if required packages are installed"""
    try:
        import PyQt5
        print("✓ PyQt5 is installed")
    except ImportError:
        print("✗ PyQt5 is not installed")
        print("Please install it with: pip install PyQt5")
        return False
    
    try:
        import mysql.connector
        print("✓ MySQL connector is installed")
    except ImportError:
        print("✗ MySQL connector is not installed")
        print("Please install it with: pip install mysql-connector-python")
        return False
    
    return True

def check_database():
    """Check if MySQL database connection is working"""
    print("Testing MySQL database connection...")
    try:
        from mysql_config import get_mysql_connection
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        # Test connection by checking if tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if len(tables) == 0:
            print("✗ Database tables not found")
            print("Creating database tables...")
            try:
                import database_setup
                database_setup.create_database()
                print("✓ Database tables created successfully")
            except Exception as e:
                print(f"✗ Failed to create database tables: {e}")
                return False
        else:
            print("✓ Database connection successful")
            print(f"✓ Found {len(tables)} database tables")
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Please check your MySQL configuration in mysql_config.py")
        print("Make sure MySQL server is running and credentials are correct")
        return False
    
    return True

def main():
    """Main function to run the POS system"""
    print("=" * 50)
    print("    STORE MANAGER POS SYSTEM")
    print("    Professional Point of Sale")
    print("=" * 50)
    print()
    
    # Check requirements
    print("Checking system requirements...")
    if not check_requirements():
        input("Press Enter to exit...")
        return
    
    # Check database
    print("Checking database...")
    if not check_database():
        input("Press Enter to exit...")
        return
    
    print()
    print("Starting POS System...")
    print("Default login: admin / admin123")
    print()
    
    # Run the main application
    try:
        import main
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()
