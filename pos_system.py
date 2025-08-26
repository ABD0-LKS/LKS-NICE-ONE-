import sys
import mysql.connector
from mysql.connector import Error
# Assuming mysql_config.py is in the same directory or accessible in PYTHONPATH
from mysql_config import get_mysql_connection
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class POSMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Store Management")
        self.setGeometry(100, 100, 1400, 900)
        self.setWindowIcon(QIcon())
        
        # Initialize database
        self.init_database()
        
        # Start with login screen
        self.show_login()
        
        # Apply modern styling
        self.setStyleSheet(self.get_modern_stylesheet())
        
    def init_database(self):
        """Initialize MySQL database with sample data"""
        self.conn = get_mysql_connection()
        if not self.conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to MySQL database")
            sys.exit(1)
            
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                code_bar VARCHAR(50),
                price_buy DECIMAL(10,2),
                price_sell DECIMAL(10,2),
                quantity INT,
                category VARCHAR(50) DEFAULT 'General'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                number INT,
                date DATETIME,
                total_price DECIMAL(10,2),
                remis DECIMAL(10,2) DEFAULT 0,
                items TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(255),
                role VARCHAR(20) DEFAULT 'seller'
            )
        ''')
        
        # Insert sample data
        sample_products = [
            ('lol', '806225247045', 80.0, 120.0, 6),
            ('nop', '661008111916', 1200.0, 1400.0, 10),
            ('champo', '307016128382', 500.0, 800.0, 1),
            ('l', '661008111916', 1200.0, 1400.0, 10),
            ('k', '508575179387', 200.0, 300.0, 120),
            ('s', '3', 100.0, 120.0, -10)
        ]
        
        for product in sample_products:
            cursor.execute('''
                INSERT IGNORE INTO products (name, code_bar, price_buy, price_sell, quantity)
                VALUES (%s, %s, %s, %s, %s)
            ''', product)
        
        # Insert sample user
        cursor.execute('''
            INSERT IGNORE INTO users (username, password, role)
            VALUES (%s, %s, %s)
        ''', ('t', 'admin', 'admin'))
        
        # Insert sample ticket
        cursor.execute('''
            INSERT IGNORE INTO tickets (number, date, total_price, items)
            VALUES (%s, %s, %s, %s)
        ''', (6, '2025-06-20 21:40:18', 120.0, '[{"name": "test", "quantity": 1, "price": 120.0}]'))
        
        self.conn.commit()
    
    def get_modern_stylesheet(self):
        return """
            QMainWindow {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
                color: white;
            }
            
            QPushButton:hover {
                opacity: 0.9;
            }
            
            QPushButton:pressed {
                opacity: 0.7;
            }
            
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #4285f4;
            }
            
            QLabel {
                color: #333;
                font-size: 14px;
            }
            
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
                font-size: 12px;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """
    
    def show_login(self):
        """Show login screen"""
        self.login_widget = LoginWidget(self)
        self.setCentralWidget(self.login_widget)
    
    def show_activation(self):
        """Show activation screen"""
        self.activation_widget = ActivationWidget(self)
        self.setCentralWidget(self.activation_widget)
    
    def show_main_menu(self):
        """Show main menu"""
        self.main_menu_widget = MainMenuWidget(self)
        self.setCentralWidget(self.main_menu_widget)
    
    def show_pos_interface(self):
        """Show main POS interface"""
        self.pos_widget = POSInterface(self)
        self.setCentralWidget(self.pos_widget)
    
    def show_dashboard(self):
        """Show dashboard"""
        self.dashboard_widget = DashboardWidget(self)
        self.setCentralWidget(self.dashboard_widget)

class LoginWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left side - Logo and branding
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: #b0bec5;")
        left_layout = QVBoxLayout()
        
        # Store Manager Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(150, 150)
        logo_pixmap.fill(QColor(52, 152, 219))
        painter = QPainter(logo_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white, 6))
        painter.drawEllipse(25, 25, 100, 100)
        painter.drawLine(50, 75, 100, 50)
        painter.drawLine(100, 50, 100, 100)
        painter.end()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("STORE MANAGER")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #4285f4; margin: 20px;")
        
        subtitle_label = QLabel("Smartware Studio")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 16px; color: #4285f4;")
        
        left_layout.addStretch()
        left_layout.addWidget(logo_label)
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        left_layout.addStretch()
        left_widget.setLayout(left_layout)
        
        # Right side - Login form
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        welcome_label = QLabel("Welcome Again !")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 32px; font-weight: bold; margin: 40px; color: #333;")
        
        # Form fields
        form_layout = QVBoxLayout()
        
        username_label = QLabel("User name :")
        username_label.setStyleSheet("font-size: 16px; margin-bottom: 5px;")
        self.username_input = QLineEdit()
        self.username_input.setText("t")
        self.username_input.setStyleSheet("font-size: 16px; padding: 15px;")
        
        password_label = QLabel("Password :")
        password_label.setStyleSheet("font-size: 16px; margin-bottom: 5px; margin-top: 20px;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("•")
        self.password_input.setStyleSheet("font-size: 16px; padding: 15px;")
        
        # Error message
        self.error_label = QLabel("Admin info was incurrect")
        self.error_label.setStyleSheet("color: #ea4335; font-size: 14px; margin: 10px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 8px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.error_label)
        form_layout.addWidget(login_btn)
        
        right_layout.addStretch()
        right_layout.addWidget(welcome_label)
        right_layout.addLayout(form_layout)
        right_layout.addStretch()
        
        # Footer
        footer_label = QLabel("© 2024 All rights reserved By Smartware,\nStudio, N 0791503305")
        footer_label.setStyleSheet("color: #666; font-size: 12px; margin: 20px;")
        right_layout.addWidget(footer_label)
        
        right_widget.setLayout(right_layout)
        
        layout.addWidget(left_widget, 1)
        layout.addWidget(right_widget, 1)
        self.setLayout(layout)
    
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        cursor = self.parent.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user:
            self.parent.show_activation()
        else:
            self.error_label.show()

class ActivationWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left side - Same logo as login
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: #b0bec5;")
        left_layout = QVBoxLayout()
        
        # Store Manager Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(150, 150)
        logo_pixmap.fill(QColor(52, 152, 219))
        painter = QPainter(logo_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white, 6))
        painter.drawEllipse(25, 25, 100, 100)
        painter.drawLine(50, 75, 100, 50)
        painter.drawLine(100, 50, 100, 100)
        painter.end()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("STORE MANAGER")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #4285f4; margin: 20px;")
        
        subtitle_label = QLabel("Smartware Studio")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 16px; color: #4285f4;")
        
        left_layout.addStretch()
        left_layout.addWidget(logo_label)
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        left_layout.addStretch()
        left_widget.setLayout(left_layout)
        
        # Right side - Activation form
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        title_label = QLabel("Get Started from here")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; margin: 40px; color: #333;")
        
        # Activation key field
        key_label = QLabel("Acivation key :")
        key_label.setStyleSheet("font-size: 16px; margin-bottom: 5px;")
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Acivation Key")
        self.key_input.setStyleSheet("font-size: 16px; padding: 15px;")
        
        # Contact info
        contact_label = QLabel("Contact Us and give this code :n+RaHNwB")
        contact_label.setStyleSheet("font-size: 14px; margin: 20px; color: #666;")
        contact_label.setAlignment(Qt.AlignCenter)
        
        # Next button
        next_btn = QPushButton("NEXT")
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 8px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        next_btn.clicked.connect(self.handle_activation)
        
        right_layout.addStretch()
        right_layout.addWidget(title_label)
        right_layout.addWidget(key_label)
        right_layout.addWidget(self.key_input)
        right_layout.addWidget(contact_label)
        right_layout.addWidget(next_btn)
        right_layout.addStretch()
        
        # Footer
        footer_label = QLabel("© 2024 All rights reserved By Smartware,\nStudio, N 0791503305")
        footer_label.setStyleSheet("color: #666; font-size: 12px; margin: 20px;")
        right_layout.addWidget(footer_label)
        
        right_widget.setLayout(right_layout)
        
        layout.addWidget(left_widget, 1)
        layout.addWidget(right_widget, 1)
        self.setLayout(layout)
    
    def handle_activation(self):
        # For demo, accept any key
        self.parent.show_main_menu()

class MainMenuWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(30)
        
        # Header with logo
        header_layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(80, 80)
        logo_pixmap.fill(QColor(52, 152, 219))
        painter = QPainter(logo_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white, 4))
        painter.drawEllipse(15, 15, 50, 50)
        painter.drawLine(30, 40, 50, 30)
        painter.drawLine(50, 30, 50, 50)
        painter.end()
        logo_label.setPixmap(logo_pixmap)
        
        title_label = QLabel("STORE MANAGER")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4285f4;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Welcome message
        welcome_label = QLabel("Welcome to SmartWere Store V 1.0")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #4285f4; margin: 40px;")
        
        # Menu buttons grid
        menu_widget = QWidget()
        menu_layout = QGridLayout()
        menu_layout.setSpacing(20)
        
        # Create menu buttons with icons
        buttons = [
            ("Dashboard(F1)", "📊", self.parent.show_dashboard),
            ("Settings (F2)", "⚙️", None),
            ("Direct sell (f3)", "🏪", self.parent.show_pos_interface),
            ("Day State (F4)", "💰", None),
            ("Seller Account (F5)", "👤", None)
        ]
        
        for i, (text, icon, callback) in enumerate(buttons):
            btn_widget = QWidget()
            btn_widget.setStyleSheet("""
                QWidget {
                    background-color: #e3f2fd;
                    border-radius: 15px;
                    border: 2px solid #bbdefb;
                }
                QWidget:hover {
                    background-color: #bbdefb;
                }
            """)
            btn_widget.setFixedSize(280, 180)
            
            btn_layout = QVBoxLayout()
            
            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("font-size: 48px; margin: 20px;")
            
            text_label = QLabel(text)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4285f4; margin: 10px;")
            
            btn_layout.addWidget(icon_label)
            btn_layout.addWidget(text_label)
            btn_widget.setLayout(btn_layout)
            
            # Make clickable
            if callback:
                btn_widget.mousePressEvent = lambda event, cb=callback: cb()
            
            row = i // 3
            col = i % 3
            menu_layout.addWidget(btn_widget, row, col)
        
        menu_widget.setLayout(menu_layout)
        
        layout.addLayout(header_layout)
        layout.addWidget(welcome_label)
        layout.addWidget(menu_widget, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        self.setLayout(layout)

class POSInterface(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.cart_items = []
        self.total = 0.0
        self.init_ui()
        self.load_products()
        
        # Timer for clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Top bar with action buttons
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left side - Product buttons (2 columns)
        left_panel = self.create_product_panel()
        content_layout.addWidget(left_panel, 2)
        
        # Center - Transaction area
        center_panel = self.create_transaction_panel()
        content_layout.addWidget(center_panel, 3)
        
        # Right side - Control buttons
        right_panel = self.create_control_panel()
        content_layout.addWidget(right_panel, 2)
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
    
    def create_top_bar(self):
        top_widget = QWidget()
        top_widget.setFixedHeight(60)
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Action buttons
        buttons_data = [
            ("Off", "#ff7043", "🖨️"),
            ("Off", "#ffab40", "⚠️"),
            ("Off", "#ff7043", "🏪"),
            ("Cuique Add", "#4caf50", "➕"),
            ("Bon D'achter", "#2196f3", "📄"),
            ("Produite List", "#ff9800", "📋"),
            ("Bon List", "#ff9800", "📄"),
            ("Returner Admin", "#ff5722", "👤")
        ]
        
        for text, color, icon in buttons_data:
            btn = QPushButton(f"{icon} {text}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            btn.setMaximumWidth(120)
            if text == "Produite List":
                btn.clicked.connect(self.show_product_list)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Date and time display
        self.datetime_widget = QWidget()
        self.datetime_widget.setStyleSheet("""
            QWidget {
                background-color: #4fc3f7;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        datetime_layout = QVBoxLayout()
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.date_label.setAlignment(Qt.AlignCenter)
        
        remis_label = QLabel("Remis")
        remis_label.setStyleSheet("color: white; font-size: 12px;")
        remis_label.setAlignment(Qt.AlignCenter)
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.time_label.setAlignment(Qt.AlignCenter)
        
        datetime_layout.addWidget(self.date_label)
        datetime_layout.addWidget(remis_label)
        datetime_layout.addWidget(self.time_label)
        self.datetime_widget.setLayout(datetime_layout)
        
        layout.addWidget(self.datetime_widget)
        top_widget.setLayout(layout)
        
        return top_widget
    
    def create_product_panel(self):
        widget = QWidget()
        self.product_layout = QGridLayout()
        self.product_layout.setSpacing(5)
        widget.setLayout(self.product_layout)
        return widget
    
    def create_transaction_panel(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Digital display
        display_widget = QWidget()
        display_widget.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px;")
        display_layout = QHBoxLayout()
        
        # Total display
        self.total_display = QLabel("120.0 DA")
        self.total_display.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: #1976d2;
                font-family: 'Courier New', monospace;
                background-color: #e3f2fd;
                padding: 20px;
                border-radius: 8px;
            }
        """)
        self.total_display.setAlignment(Qt.AlignCenter)
        
        # Calculate Rest button
        calc_btn = QPushButton("Calcule Rest")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #4fc3f7;
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        # Rest display
        rest_display = QLabel("0")
        rest_display.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #1976d2;
                font-family: 'Courier New', monospace;
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 8px;
            }
        """)
        rest_display.setAlignment(Qt.AlignCenter)
        
        display_layout.addWidget(self.total_display, 2)
        display_layout.addWidget(calc_btn)
        display_layout.addWidget(rest_display, 1)
        display_widget.setLayout(display_layout)
        
        # Search bar
        search_widget = QWidget()
        search_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Rechercher Produite")
        search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 8px;
                border: 2px solid #e0e0e0;
                font-size: 14px;
                background-color: #f5f5f5;
            }
        """)
        search_layout.addWidget(search_input)
        search_widget.setLayout(search_layout)
        
        # Client tabs
        client_widget = QWidget()
        client_layout = QHBoxLayout()
        
        nouveau_btn = QPushButton("Nouveau Client")
        nouveau_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
        """)
        
        client1_btn = QPushButton("Client #1")
        client1_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
        """)
        
        client_layout.addWidget(nouveau_btn)
        client_layout.addWidget(client1_btn)
        client_layout.addStretch()
        client_widget.setLayout(client_layout)
        
        # Transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels([
            "Nom", "Prix", "Quantity Achter", "Quantity in Stock", "Totale Prix", "Action"
        ])
        self.transaction_table.horizontalHeader().setStretchLastSection(True)
        self.transaction_table.setAlternatingRowColors(True)
        self.transaction_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)
        
        layout.addWidget(display_widget)
        layout.addWidget(search_widget)
        layout.addWidget(client_widget)
        layout.addWidget(self.transaction_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_control_panel(self):
        widget = QWidget()
        layout = QGridLayout()
        layout.setSpacing(5)
        
        # Control buttons with exact colors and layout from screenshot
        buttons = [
            ("📦\nMultiple", "#ff9800", 0, 0),
            ("⬆️", "#e91e63", 0, 1),
            ("🔙\nback produi", "#2196f3", 0, 2),
            ("⬅️", "#e91e63", 1, 0),
            ("✅", "#4caf50", 1, 1),
            ("➡️", "#e91e63", 1, 2),
            ("⌨️\nClavier", "#ff9800", 2, 0),
            ("⬇️", "#e91e63", 2, 1),
            ("👤\nClient", "#ff9800", 2, 2),
            ("🛒\nDelete", "#ff9800", 3, 0),
            ("🧹\nCleare", "#ff9800", 3, 1),
            ("🧮\nCalculatrice", "#2196f3", 3, 2),
            ("🔄\nUpdate", "#4caf50", 4, 0),
            ("🎫\nNew Ticket", "#2196f3", 4, 1),
            ("🗑️\nDelete", "#f44336", 4, 2),
        ]
        
        for text, color, row, col in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    font-weight: bold;
                    font-size: 10px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            btn.setMinimumSize(80, 70)
            layout.addWidget(btn, row, col)
        
        widget.setLayout(layout)
        return widget
    
    def load_products(self):
        """Load products from database and create buttons"""
        cursor = self.parent.conn.cursor()
        cursor.execute('SELECT * FROM products LIMIT 12')  # Limit for grid layout
        products = cursor.fetchall()
        
        row, col = 0, 0
        for product in products:
            btn = QPushButton(product[1])  # product name
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4fc3f7;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 20px;
                    font-weight: bold;
                    font-size: 14px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #29b6f6;
                }
            """)
            btn.setMinimumSize(120, 100)
            btn.clicked.connect(lambda checked, p=product: self.add_to_cart(p))
            
            self.product_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= 2:  # 2 columns as shown in screenshot
                col = 0
                row += 1
    
    def add_to_cart(self, product):
        """Add product to cart"""
        # Check if product already in cart
        for item in self.cart_items:
            if item['id'] == product[0]:
                item['quantity'] += 1
                break
        else:
            # Add new item
            self.cart_items.append({
                'id': product[0],
                'name': product[1],
                'price': product[4],  # price_sell
                'quantity': 1,
                'stock': product[5]
            })
        
        self.update_transaction_table()
        self.update_total()
    
    def update_transaction_table(self):
        """Update the transaction table"""
        self.transaction_table.setRowCount(len(self.cart_items))
        
        for row, item in enumerate(self.cart_items):
            self.transaction_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.transaction_table.setItem(row, 1, QTableWidgetItem(f"{item['price']:.1f}"))
            self.transaction_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            
            # Stock with color coding
            stock_item = QTableWidgetItem(str(item['stock']))
            if item['stock'] < 0:
                stock_item.setBackground(QColor(255, 235, 238))
                stock_item.setForeground(QColor(211, 47, 47))
            self.transaction_table.setItem(row, 3, stock_item)
            
            self.transaction_table.setItem(row, 4, QTableWidgetItem(f"{item['price'] * item['quantity']:.1f}"))
            
            # Remove button
            remove_btn = QPushButton("X")
            remove_btn.setStyleSheet("background-color: #f44336; color: white; border-radius: 4px; padding: 5px;")
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.transaction_table.setCellWidget(row, 5, remove_btn)
    
    def remove_from_cart(self, row):
        """Remove item from cart"""
        if 0 <= row < len(self.cart_items):
            del self.cart_items[row]
            self.update_transaction_table()
            self.update_total()
    
    def update_total(self):
        """Update total display"""
        self.total = sum(item['price'] * item['quantity'] for item in self.cart_items)
        self.total_display.setText(f"{self.total:.1f} DA")
    
    def update_clock(self):
        """Update date and time display"""
        now = datetime.now()
        self.date_label.setText(now.strftime("%d/%m/%Y"))
        self.time_label.setText(now.strftime("%H:%M:%S"))
    
    def show_product_list(self):
        """Show product list dialog"""
        dialog = ProductListDialog(self.parent)
        dialog.exec_()

class ProductListDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Product List")
        self.setModal(True)
        self.resize(1000, 600)
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Product List")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        # Search and controls
        controls_layout = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Rechercher Produites")
        search_input.setStyleSheet("padding: 10px; border-radius: 8px; border: 2px solid #e0e0e0;")
        
        filter_btn = QPushButton("Filter :")
        filter_btn.setStyleSheet("background-color: #666; color: white; padding: 10px; border-radius: 8px;")
        
        export_btn = QPushButton("📄 Export")
        export_btn.setStyleSheet("background-color: #4caf50; color: white; padding: 10px; border-radius: 8px;")
        
        add_btn = QPushButton("➕ Ajouter Product")
        add_btn.setStyleSheet("background-color: #2e7d32; color: white; padding: 10px; border-radius: 8px;")
        add_btn.clicked.connect(self.show_add_product)
        
        controls_layout.addWidget(search_input)
        controls_layout.addStretch()
        controls_layout.addWidget(filter_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addWidget(add_btn)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels([
            "Nom", "Code bar", "Prix acheter", "Prix Ventre", "Quantite", "Actions"
        ])
        self.products_table.horizontalHeader().setStretchLastSection(True)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        close_bottom_btn = QPushButton("Close")
        close_bottom_btn.setStyleSheet("background-color: #666; color: white; padding: 10px 20px; border-radius: 8px;")
        close_bottom_btn.clicked.connect(self.close)
        
        done_btn = QPushButton("Done")
        done_btn.setStyleSheet("background-color: #4285f4; color: white; padding: 10px 20px; border-radius: 8px;")
        done_btn.clicked.connect(self.close)
        
        bottom_layout.addWidget(close_bottom_btn)
        bottom_layout.addWidget(done_btn)
        
        layout.addLayout(header_layout)
        layout.addLayout(controls_layout)
        layout.addWidget(self.products_table)
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
    
    def load_products(self):
        """Load products into table"""
        cursor = self.parent.conn.cursor()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(product[1]))  # name
            self.products_table.setItem(row, 1, QTableWidgetItem(product[2] or ""))  # code_bar
            self.products_table.setItem(row, 2, QTableWidgetItem(f"{product[3]:.1f}"))  # price_buy
            self.products_table.setItem(row, 3, QTableWidgetItem(f"{product[4]:.1f}"))  # price_sell
            
            # Quantity with color coding
            quantity_item = QTableWidgetItem(str(product[5]))
            if product[5] < 0:
                quantity_item.setBackground(QColor(255, 235, 238))
                quantity_item.setForeground(QColor(211, 47, 47))
            self.products_table.setItem(row, 4, quantity_item)
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("background-color: #00bcd4; color: white; padding: 5px 10px; border-radius: 4px;")
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px 10px; border-radius: 4px;")
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_widget.setLayout(actions_layout)
            
            self.products_table.setCellWidget(row, 5, actions_widget)
    
    def show_add_product(self):
        """Show add product dialog"""
        dialog = ProductAddDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            self.load_products()

class ProductAddDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Product Add")
        self.setModal(True)
        self.resize(500, 700)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Product Add")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        # Form fields
        form_layout = QFormLayout()
        
        # Code bar
        self.code_bar_input = QLineEdit()
        self.code_bar_input.setText("661008111916")
        self.code_bar_input.setStyleSheet("padding: 10px; border-radius: 8px; border: 2px solid #e0e0e0;")
        
        # Barcode buttons
        barcode_layout = QHBoxLayout()
        generate_btn = QPushButton("Generer")
        generate_btn.setStyleSheet("background-color: #2196f3; color: white; padding: 8px; border-radius: 4px;")
        
        print_btn = QPushButton("Imprimer")
        print_btn.setStyleSheet("background-color: #4caf50; color: white; padding: 8px; border-radius: 4px;")
        
        barcode_layout.addWidget(generate_btn)
        barcode_layout.addWidget(print_btn)
        barcode_layout.addStretch()
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setText("1")
        self.name_input.setStyleSheet("padding: 10px; border-radius: 8px; border: 2px solid #e0e0e0;")
        
        # Price Sell
        self.price_sell_input = QLineEdit()
        self.price_sell_input.setText("1400")
        self.price_sell_input.setStyleSheet("padding: 10px; border-radius: 8px; border: 2px solid #e0e0e0;")
        
        # Price Buy
        self.price_buy_input = QLineEdit()
        self.price_buy_input.setText("1200")
        self.price_buy_input.setStyleSheet("padding: 10px; border-radius: 8px; border: 2px solid #e0e0e0;")
        
        # Quantity
        self.quantity_input = QLineEdit()
        self.quantity_input.setText("10")
        self.quantity_input.setStyleSheet("padding: 10px; border-radius: 8px; border: 2px solid #e0e0e0;")
        
        form_layout.addRow("Code bar", self.code_bar_input)
        form_layout.addRow("", barcode_layout)
        form_layout.addRow("Name :", self.name_input)
        form_layout.addRow("Price Sell:", self.price_sell_input)
        form_layout.addRow("Price Buy:", self.price_buy_input)
        form_layout.addRow("Quantity :", self.quantity_input)
        
        # Benefit labels
        self.benefit_label = QLabel("Benefit per piece: 200.00 DA")
        self.benefit_label.setStyleSheet("color: #2196f3; font-weight: bold; margin: 10px;")
        
        self.total_benefit_label = QLabel("Benefit per piece: 2000.00 DA")
        self.total_benefit_label.setStyleSheet("color: #2196f3; font-weight: bold; margin: 10px;")
        
        # Barcode display
        barcode_widget = QWidget()
        barcode_widget.setFixedHeight(80)
        barcode_widget.setStyleSheet("background-color: #f5f5f5; border: 2px dashed #ccc; border-radius: 8px;")
        barcode_layout_display = QVBoxLayout()
        barcode_label = QLabel("|||||||||||||||||||")
        barcode_label.setAlignment(Qt.AlignCenter)
        barcode_label.setStyleSheet("font-family: 'Courier New'; font-size: 20px; font-weight: bold;")
        barcode_layout_display.addWidget(barcode_label)
        barcode_widget.setLayout(barcode_layout_display)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        close_bottom_btn = QPushButton("Close")
        close_bottom_btn.setStyleSheet("background-color: #666; color: white; padding: 10px 20px; border-radius: 8px;")
        close_bottom_btn.clicked.connect(self.close)
        
        done_btn = QPushButton("Done")
        done_btn.setStyleSheet("background-color: #4285f4; color: white; padding: 10px 20px; border-radius: 8px;")
        done_btn.clicked.connect(self.save_product)
        
        bottom_layout.addWidget(close_bottom_btn)
        bottom_layout.addWidget(done_btn)
        
        # Connect inputs for benefit calculation
        self.price_sell_input.textChanged.connect(self.calculate_benefit)
        self.price_buy_input.textChanged.connect(self.calculate_benefit)
        self.quantity_input.textChanged.connect(self.calculate_benefit)
        
        layout.addLayout(header_layout)
        layout.addLayout(form_layout)
        layout.addWidget(self.benefit_label)
        layout.addWidget(self.total_benefit_label)
        layout.addWidget(barcode_widget)
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        self.calculate_benefit()
    
    def calculate_benefit(self):
        """Calculate and display benefit"""
        try:
            price_sell = float(self.price_sell_input.text() or 0)
            price_buy = float(self.price_buy_input.text() or 0)
            quantity = int(self.quantity_input.text() or 0)
            
            benefit_per_piece = price_sell - price_buy
            total_benefit = benefit_per_piece * quantity
            
            self.benefit_label.setText(f"Benefit per piece: {benefit_per_piece:.2f} DA")
            self.total_benefit_label.setText(f"Benefit per piece: {total_benefit:.2f} DA")
        except ValueError:
            pass
    
    def save_product(self):
        """Save product to database"""
        try:
            name = self.name_input.text().strip()
            code_bar = self.code_bar_input.text().strip()
            price_buy = float(self.price_buy_input.text() or 0)
            price_sell = float(self.price_sell_input.text() or 0)
            quantity = int(self.quantity_input.text() or 0)
            
            if not name:
                QMessageBox.warning(self, "Error", "Product name is required!")
                return
            
            cursor = self.parent.conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, code_bar, price_buy, price_sell, quantity)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, code_bar, price_buy, price_sell, quantity))
            
            self.parent.conn.commit()
            self.accept()
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values!")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "This barcode already exists!")

class DashboardWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header with back button
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("←")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        back_btn.setFixedSize(40, 40)
        back_btn.clicked.connect(self.parent.show_main_menu)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        
        # Sidebar
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(250)
        sidebar_widget.setStyleSheet("background-color: white; border-radius: 10px;")
        sidebar_layout = QVBoxLayout()
        
        # Sidebar items
        sidebar_items = [
            ("🏠 Dashboard", True),
            ("📦 Products", False),
            ("🎫 Tickets", False)
        ]
        
        for text, active in sidebar_items:
            btn = QPushButton(text)
            if active:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e3f2fd;
                        color: #1976d2;
                        border: none;
                        padding: 15px;
                        text-align: left;
                        font-weight: bold;
                        border-radius: 8px;
                        margin: 5px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #666;
                        border: none;
                        padding: 15px;
                        text-align: left;
                        border-radius: 8px;
                        margin: 5px;
                    }
                    QPushButton:hover {
                        background-color: #f5f5f5;
                    }
                """)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        sidebar_widget.setLayout(sidebar_layout)
        
        # Main content
        main_content = QWidget()
        content_layout = QVBoxLayout()
        
        # KPI Cards
        kpi_layout = QHBoxLayout()
        
        kpis = [
            ("Benifist", "260.00", "#4caf50", "📈"),
            ("Pruduite Vendre", "5", "#ff9800", "🛒"),
            ("Capital", "36780.00", "#2196f3", "💰"),
            ("N poduite", "4", "#4caf50", "📦")
        ]
        
        for title, value, color, icon in kpis:
            card = self.create_kpi_card(title, value, color, icon)
            kpi_layout.addWidget(card)
        
        # Charts
        charts_layout = QHBoxLayout()
        
        # Daily Sales Chart
        daily_chart = self.create_chart("Daily Sales", ["2025-06-20"], [2.0])
        charts_layout.addWidget(daily_chart)
        
        # Top Products Chart
        top_chart = self.create_chart("Top 7 Products", ["tt", "2"], [4.0, 1.0])
        charts_layout.addWidget(top_chart)
        
        content_layout.addLayout(kpi_layout)
        content_layout.addLayout(charts_layout)
        content_layout.addStretch()
        main_content.setLayout(content_layout)
        
        # Combine sidebar and main content
        main_layout = QHBoxLayout()
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(main_content)
        
        layout.addLayout(header_layout)
        layout.addLayout(main_layout)
        
        self.setLayout(layout)
    
    def create_kpi_card(self, title, value, color, icon):
        """Create KPI card widget"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        card.setFixedHeight(120)
        
        layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px; color: {color}; margin: 10px;")
        
        # Text
        text_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #666; margin-bottom: 5px;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        text_layout.addStretch()
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        card.setLayout(layout)
        return card
    
    def create_chart(self, title, labels, data):
        """Create chart widget"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e0e0e0;")
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 15px; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Simple chart representation using colored bars
        chart_widget = QWidget()
        chart_widget.setFixedHeight(200)
        chart_layout = QVBoxLayout()
        
        # Create simple bar representation
        for i, (label, value) in enumerate(zip(labels, data)):
            bar_layout = QHBoxLayout()
            
            label_widget = QLabel(label)
            label_widget.setFixedWidth(80)
            label_widget.setStyleSheet("font-size: 12px; color: #666;")
            
            bar_widget = QWidget()
            bar_width = int(value * 50)  # Scale for display
            bar_widget.setFixedSize(bar_width, 20)
            bar_widget.setStyleSheet("background-color: #ff7043; border-radius: 4px;")
            
            bar_layout.addWidget(label_widget)
            bar_layout.addWidget(bar_widget)
            bar_layout.addStretch()
            
            chart_layout.addLayout(bar_layout)
        
        chart_layout.addStretch()
        chart_widget.setLayout(chart_layout)
        
        layout.addWidget(title_label)
        layout.addWidget(chart_widget)
        
        widget.setLayout(layout)
        return widget

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("Store Management")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Smartware Studio")
    
    # Create main window
    window = POSMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
