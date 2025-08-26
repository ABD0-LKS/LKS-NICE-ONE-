import mysql.connector
from mysql.connector import Error
import os

def get_mysql_connection():
    """Get MySQL database connection"""
    try:
        config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', 'HRMMSSL1234'),
            'database': os.getenv('MYSQL_DATABASE', 'pos_database'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': False
        }
        
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            return connection
        else:
            raise Error("Failed to connect to MySQL database")
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def close_connection(connection):
    """Close MySQL database connection"""
    if connection and connection.is_connected():
        connection.close()

class MySQLConnectionManager:
    """Context manager for MySQL connections"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        self.connection = get_mysql_connection()
        if self.connection:
            self.cursor = self.connection.cursor()
            return self.cursor, self.connection
        else:
            raise Error("Failed to establish MySQL connection")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if self.connection:
                self.connection.rollback()
        else:
            if self.connection:
                self.connection.commit()
        
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
