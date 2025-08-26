import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_mysql_config():
    """Get MySQL database configuration"""
    return {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': os.getenv('MYSQL_PORT', 3306),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', 'HRMMSSL1234'),
        'database': os.getenv('MYSQL_DATABASE', 'pos_database'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }

def create_database():
    """Create and initialize the POS database"""
    config = get_mysql_config()
    
    try:
        server_config = config.copy()
        database_name = server_config.pop('database')
        
        conn = mysql.connector.connect(**server_config)
        cursor = conn.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        cursor.execute(f"USE {database_name}")
        
        print("Creating database tables...")
        
        # Create all tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unknown_barcodes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                barcode VARCHAR(255) NOT NULL,
                scan_date DATETIME NOT NULL,
                resolved TINYINT DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'cashier',
                full_name VARCHAR(100),
                email VARCHAR(100),
                created_date DATETIME,
                last_login DATETIME
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                code_bar VARCHAR(50),
                price_buy DECIMAL(10,2) DEFAULT 0,
                price_sell DECIMAL(10,2) NOT NULL,
                quantity INT DEFAULT 0,
                category VARCHAR(50) DEFAULT 'General',
                created_date DATETIME,
                updated_date DATETIME
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100),
                address TEXT,
                created_date DATETIME,
                total_purchases DECIMAL(10,2) DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticket_number VARCHAR(50) UNIQUE,
                date DATETIME NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                remis DECIMAL(10,2) DEFAULT 0,
                payment_method VARCHAR(20) DEFAULT 'Cash',
                customer_name VARCHAR(255),
                items TEXT,
                status VARCHAR(20) DEFAULT 'Completed',
                cashier_id INT,
                FOREIGN KEY (cashier_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticket_id INT,
                product_id INT,
                quantity INT,
                unit_price DECIMAL(10,2),
                total_price DECIMAL(10,2),
                date DATETIME,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                `key` VARCHAR(100) UNIQUE NOT NULL,
                value TEXT,
                description TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE UNIQUE NOT NULL,
                total_sales DECIMAL(10,2) DEFAULT 0,
                total_transactions INT DEFAULT 0,
                total_items_sold INT DEFAULT 0,
                created_date DATETIME
            )
        ''')
        
        print("Checking for existing data...")
        
        # Check if admin user already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        admin_exists = cursor.fetchone()[0] > 0
        
        if not admin_exists:
            print("Inserting sample data...")
            
            # Insert admin user
            cursor.execute('''
                INSERT INTO users (username, password, role, full_name, email, created_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', ('admin', 'admin123', 'admin', 'System Administrator', 'admin@store.com', datetime.now()))
            
            # Insert sample products
            sample_products = [
                ('Coca Cola 330ml', '1234567890123', 25.0, 35.0, 50, 'Beverages'),
                ('Bread', '2345678901234', 15.0, 25.0, 30, 'Bakery'),
                ('Milk 1L', '3456789012345', 45.0, 60.0, 25, 'Dairy'),
                ('Rice 1kg', '4567890123456', 80.0, 120.0, 40, 'Grains'),
                ('Chicken 1kg', '5678901234567', 350.0, 450.0, 15, 'Meat'),
                ('Tomatoes 1kg', '6789012345678', 60.0, 90.0, 20, 'Vegetables'),
                ('Apples 1kg', '7890123456789', 120.0, 180.0, 18, 'Fruits'),
                ('Shampoo', '8901234567890', 180.0, 250.0, 12, 'Personal Care'),
                ('Soap', '9012345678901', 35.0, 50.0, 25, 'Personal Care'),
                ('Pasta 500g', '0123456789012', 45.0, 70.0, 35, 'Grains')
            ]
            
            for product in sample_products:
                cursor.execute('''
                    INSERT INTO products (name, code_bar, price_buy, price_sell, quantity, category, created_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (*product, datetime.now()))
            
            # Insert sample customers
            sample_customers = [
                ('Ahmed Benali', '0555123456', 'ahmed@email.com', '123 Main St, Algiers'),
                ('Fatima Khelil', '0666789012', 'fatima@email.com', '456 Oak Ave, Oran'),
                ('Mohamed Saidi', '0777345678', 'mohamed@email.com', '789 Pine Rd, Constantine'),
                ('Amina Bouazza', '0888901234', 'amina@email.com', '321 Elm St, Annaba'),
                ('Youssef Hamdi', '0999567890', 'youssef@email.com', '654 Cedar Blvd, Setif')
            ]
            
            for customer in sample_customers:
                cursor.execute('''
                    INSERT INTO customers (name, phone, email, address, created_date)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (*customer, datetime.now()))
            
            # Insert system settings
            settings = [
                ('store_name', 'Smart Store', 'Store name'),
                ('store_address', '123 Business Street, Algiers, Algeria', 'Store address'),
                ('store_phone', '+213 555 123 456', 'Store phone number'),
                ('store_email', 'info@smartstore.dz', 'Store email'),
                ('currency', 'DA', 'Currency symbol'),
                ('tax_rate', '19', 'Tax rate percentage'),
                ('receipt_footer', 'Thank you for shopping with us!', 'Receipt footer message'),
                ('low_stock_threshold', '10', 'Low stock alert threshold')
            ]
            
            for setting in settings:
                cursor.execute('''
                    INSERT INTO settings (`key`, value, description)
                    VALUES (%s, %s, %s)
                ''', setting)
            
            # Insert sample tickets
            sample_tickets = [
                ('TKT000001', datetime.now(), 155.0, 0, 'Cash', 'Ahmed Benali', 
                 '[{"name": "Coca Cola 330ml", "quantity": 2, "price": 35.0, "total": 70.0}, {"name": "Bread", "quantity": 1, "price": 25.0, "total": 25.0}, {"name": "Milk 1L", "quantity": 1, "price": 60.0, "total": 60.0}]'),
                ('TKT000002', datetime.now(), 270.0, 0, 'Cash', 'Walk-in Customer',
                 '[{"name": "Rice 1kg", "quantity": 1, "price": 120.0, "total": 120.0}, {"name": "Chicken 1kg", "quantity": 1, "price": 450.0, "total": 450.0}]')
            ]
            
            for ticket in sample_tickets:
                cursor.execute('''
                    INSERT INTO tickets (ticket_number, date, total_price, remis, payment_method, customer_name, items, status, cashier_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (*ticket, 'Completed', 1))
        else:
            print("Sample data already exists. Skipping insertion.")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database setup completed successfully!")
        print("Default login: admin / admin123")
        print(f"MySQL Database: {database_name}")
        
    except Error as e:
        print(f"Error creating MySQL database: {e}")
        try:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
        except:
            pass


if __name__ == '__main__':
    create_database()