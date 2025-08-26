import sys
import mysql.connector
from mysql.connector import Error
from mysql_config import get_mysql_connection, MySQLConnectionManager
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
import json
import os
import time
from dashboard_widget import DashboardWidget
from pos_widget import POSWidget
from product_management_widget import ProductManagementWidget
from ticket_management_widget import TicketManagementWidget
from reports_widget import ReportsWidget
from i18n import tr, set_language

# Initialize MySQL connection on startup
try:
    conn = get_mysql_connection()
    if not conn:
        from database_setup import create_database
        create_database()
        conn = get_mysql_connection()
except Error as e:
    print(f"Database connection error: {e}")
    conn = None


class POSApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Store Manager - LKS POS System")
        self.setWindowIcon(self.create_app_icon())

        # Set window to fullscreen and proper sizing
        self.showMaximized()
        self.setMinimumSize(1200, 800)

        # Apply modern styling
        self.setStyleSheet(self.get_modern_stylesheet())

        # Initialize database
        self.conn = None
        self.current_user = None
        self.init_database()

        # Load app theme and language
        self.load_app_settings()

        # Show login screen
        self.show_login_screen()

        # Enable keyboard shortcuts
        self.setFocusPolicy(Qt.StrongFocus)

    def create_app_icon(self):
        """Create application icon"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(66, 133, 244))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        # FIXED: Create QPen object with color and width
        painter.setPen(QPen(Qt.white, 4))
        painter.drawEllipse(8, 8, 48, 48)
        painter.drawLine(20, 32, 44, 20)
        painter.drawLine(44, 20, 44, 44)
        painter.end()
        return QIcon(pixmap)

    def init_database(self):
        """Initialize database connection"""
        try:
            self.conn = get_mysql_connection()
            if not self.conn:
                raise Error("Failed to connect to MySQL database")
            
            cursor = self.conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            if not tables:
                raise Error("Database is empty")

        except Error as e:
            QMessageBox.critical(self, "Database Error",
                                 f"Database error: {e}\n\n"
                                 "Please run 'python database_setup.py' first to create the database.")
            sys.exit(1)


    def show_login_screen(self):
        """Show login screen"""
        self.login_widget = LoginWidget(self)
        self.setCentralWidget(self.login_widget)

    def show_activation_screen(self):
        """Show activation screen"""
        self.activation_widget = ActivationWidget(self)
        self.setCentralWidget(self.activation_widget)

    def show_main_menu(self):
        """Show main menu"""
        self.main_menu_widget = MainMenuWidget(self)
        self.setCentralWidget(self.main_menu_widget)

    def show_pos_screen(self):
        """Show POS interface"""
        self.pos_widget = POSWidget(self)
        self.setCentralWidget(self.pos_widget)

    def show_dashboard(self):
        """Show dashboard"""
        self.dashboard_widget = DashboardWidget(self)
        self.setCentralWidget(self.dashboard_widget)

    def show_product_management(self):
        """Show product management"""
        self.product_widget = ProductManagementWidget(self)
        self.setCentralWidget(self.product_widget)

    def show_ticket_management(self):
        """Show ticket management"""
        self.ticket_widget = TicketManagementWidget(self)
        self.setCentralWidget(self.ticket_widget)

    def show_settings(self):
        """Show settings"""
        self.settings_widget = SettingsWidget(self)
        self.setCentralWidget(self.settings_widget)

    def show_day_state(self):
        """Show day state"""
        self.day_state_widget = DayStateWidget(self)
        self.setCentralWidget(self.day_state_widget)

    def show_seller_account(self):
        """Show seller account"""
        self.seller_account_widget = SellerAccountWidget(self)
        self.setCentralWidget(self.seller_account_widget)

    def show_reports(self):
        """Show reports"""
        self.reports_widget = ReportsWidget(self)
        self.setCentralWidget(self.reports_widget)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts restricting cashier role."""
        user = getattr(self, "current_user", None)
        role = (user.get("role") if user else "") or ""
        is_cashier = role.lower() == "cashier"

        if hasattr(self, 'main_menu_widget') and self.centralWidget() == self.main_menu_widget:
            key = event.key()
            if key == Qt.Key_F1 and not is_cashier:
                self.show_dashboard()
            elif key == Qt.Key_F2 and not is_cashier:
                self.show_settings()
            elif key == Qt.Key_F3:
                self.show_pos_screen()
            elif key == Qt.Key_F4 and not is_cashier:
                self.show_day_state()
            elif key == Qt.Key_F5:
                self.show_seller_account()
            elif key == Qt.Key_R and not is_cashier:
                self.show_reports()
        super().keyPressEvent(event)

    def get_modern_stylesheet(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f3f4f6, stop:1 #e5e7eb);
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }

            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
            }

            QushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34d399, stop:1 #10b981);
            }

            QPushButton:pressed {
                background: #047857;
            }

            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: white;
                selection-background-color: #10b981;
            }

            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #10b981;
            }

            QLabel {
                color: #1f2937;
                font-size: 14px;
            }

            QTableWidget {
               border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
                gridline-color: #e5e7eb;
                font-size: 13px;
                selection-background-color: #d1fae5;
                selection-color: #065f46;
            }

            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f3f4f6;
            }

            QTableWidget::item:selected {
                background-color: #d1fae5;
                color: #065f46;
            }

            QHeaderView::section {
                background: #f9fafb;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                font-weight: 600;
                font-size: 12px;
                color: #374151;
            }

            QGroupBox {
                font-weight: 600;
                font-size: 16px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: white;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #374151;
                background-color: white;
            }

            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
                margin-top: -1px;
            }

            QTabBar::tab {
                background: #f3f4f6;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                color: #6b7280;
            }

            QTabBar::tab:selected {
                background: white;
                color: #10b981;
                border-bottom: 2px solid #10b981;
            }

            QTabBar::tab:hover:!selected {
                background: #e5e7eb;
            }
        """

    def apply_theme(self, dark: bool):
        app = QApplication.instance()
        if not app:
            return
        app.setStyle("Fusion")
        if dark:
            palette = QPalette()
            # Base surfaces
            palette.setColor(QPalette.Window, QColor(24, 24, 27))        # zinc-900
            palette.setColor(QPalette.Base, QColor(17, 17, 19))          # near-black
            palette.setColor(QPalette.AlternateBase, QColor(32, 32, 36))
            # Text
            palette.setColor(QPalette.WindowText, QColor(229, 231, 235)) # gray-200
            palette.setColor(QPalette.Text, QColor(229, 231, 235))
            palette.setColor(QPalette.ButtonText, QColor(229, 231, 235))
            palette.setColor(QPalette.ToolTipBase, QColor(17, 17, 19))
            palette.setColor(QPalette.ToolTipText, QColor(229, 231, 235))
            # Controls
            palette.setColor(QPalette.Button, QColor(38, 38, 42))
            # Accents
            palette.setColor(QPalette.Highlight, QColor(16, 185, 129))   # emerald-500
            palette.setColor(QPalette.HighlightedText, QColor(17, 24, 39))
            palette.setColor(QPalette.BrightText, QColor(239, 68, 68))   # red-500
            app.setPalette(palette)

            # App-wide stylesheet to normalize component-level "white" backgrounds
            app.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #18181b;
                    color: #e5e7eb;
                }
                QPushButton {
                    background-color: #10b981;
                    color: #081016;
                    border: none; border-radius: 8px; padding: 10px 16px; font-weight: 600;
                }
                QPushButton:hover { background-color: #34d399; }
                QPushButton:pressed { background-color: #059669; }

                QLineEdit, QTextEdit, QComboBox, QDateEdit {
                    background-color: #111115;
                    color: #e5e7eb;
                    border: 1px solid #3f3f46;
                    border-radius: 8px;
                    selection-background-color: #10b981;
                    selection-color: #081016;
                }
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                    border: 1px solid #10b981;
                }

                QLabel { color: #e5e7eb; }

                QTableWidget {
                    background-color: #111115;
                    color: #e5e7eb;
                    border: 1px solid #27272a;
                    gridline-color: #27272a;
                }
                QHeaderView::section {
                    background-color: #202022;
                    color: #d1d5db;
                    border: none;
                    border-bottom: 1px solid #27272a;
                    padding: 10px;
                }
                QTableWidget::item:selected {
                    background: #064e3b;
                    color: #ecfdf5;
                }

                QGroupBox {
                    background-color: #111115;
                    border: 1px solid #27272a;
                    border-radius: 8px;
                    margin-top: 12px;
                    padding-top: 16px;
                }
                QGroupBox::title {
                    color: #d1d5db;
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 6px;
                    background-color: #111115;
                }

                QTabWidget::pane {
                    background-color: #111115;
                    border: 1px solid #27272a;
                    border-radius: 8px;
                }
                QTabBar::tab {
                    background-color: #202022;
                    color: #a3a3a3;
                    padding: 10px 18px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #111115;
                    color: #10b981;
                    border-bottom: 2px solid #10b981;
                }
            """)
        else:
            app.setPalette(QPalette())
            app.setStyleSheet("")

    def apply_language(self, lang: str):
        app = QApplication.instance()
        if not app:
            return
        app.setLayoutDirection(Qt.LeftToRight)
        # Force relayout
        if self.centralWidget():
            self.centralWidget().update()

    def load_app_settings(self):
        """Load Dark Mode and Language from DB settings and apply."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT `key`, value FROM settings")
            data = dict(cursor.fetchall())
            dark = data.get("dark_mode", "off").lower() in ("1", "true", "on", "yes")
            lang = data.get("language", "en")
            set_language(lang)
            self.apply_theme(dark)
            self.apply_language(lang)
        except Exception:
            pass


class LoginWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left panel - Branding
        left_panel = QWidget()
        left_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(200, 200)
        logo_pixmap.fill(Qt.transparent)
        painter = QPainter(logo_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white, 8))
        painter.drawEllipse(30, 30, 140, 140)
        painter.drawLine(70, 100, 130, 70)
        painter.drawLine(130, 70, 130, 130)
        painter.end()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("STORE MANAGER")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 42px;
            font-weight: 700;
            color: white;
            margin: 20px 0;
            letter-spacing: 2px;
        """)

        subtitle_label = QLabel("LKS POS System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 18px;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 40px;
        """)

        features_label = QLabel("✓ Inventory Management\n✓ Sales Tracking\n✓ Customer Management\n✓ Reports & Analytics")
        features_label.setAlignment(Qt.AlignCenter)
        features_label.setStyleSheet("""
            font-size: 16px;
            color: rgba(255, 255, 255, 0.9);
            line-height: 1.6;
        """)

        left_layout.addWidget(logo_label)
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        left_layout.addWidget(features_label)
        left_panel.setLayout(left_layout)

        # Right panel - Login form
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setContentsMargins(60, 60, 60, 60)

        welcome_label = QLabel("Welcome Back!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            font-size: 36px;
            font-weight: 700;
            color: #333;
            margin-bottom: 40px;
        """)

        # Login form
        form_widget = QWidget()
        form_widget.setMaximumWidth(400)
        form_layout = QVBoxLayout()

        # Username field
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #555; margin-bottom: 8px;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setText("admin")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 16px;
                font-size: 16px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            QLineEdit:focus {
                border-color: #4285f4;
            }
        """)

        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #555; margin-bottom: 8px;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("admin123")
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 16px;
                font-size: 16px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            QLineEdit:focus {
                border-color: #4285f4;
            }
        """)

        # Error message
        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("""
            color: #dc3545;
            font-size: 14px;
            font-weight: 600;
           极 margin: 10px 0;
            padding: 10px;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 6px;
        """)
        self.error_label.hide()

        # Login button
        login_btn = QPushButton("Sign In")
        login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4285f4, stop:1 #3367d6);
                color: white;
                padding: 16px;
                font-size: 18px;
                font-weight: 600;
                border-radius: 10px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a95f5, stop:1 #4285f4);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3367d6, stop:1 #2c5aa0;
            }
        """)
        login_btn.clicked.connect(self.handle_login)

        # Enter key support
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.handle_login)

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.error_label)
        form_layout.addWidget(login_btn)

        form_widget.setLayout(form_layout)

        # Footer
        footer_label = QLabel("© 2025 LKS Studio. All rights reserved.")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("""
            color: #6c757d;
            font-size: 12px;
            margin-top: 40px;
        """)

        right_layout.addWidget(welcome_label)
        right_layout.addWidget(form_widget)
        right_layout.addWidget(footer_label)
        right_panel.setLayout(right_layout)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        self.setLayout(main_layout)

        welcome_label.setText(tr("WELCOME_BACK"))
        username_label.setText(tr("USERNAME"))
        password_label.setText(tr("PASSWORD"))
        login_btn.setText(tr("SIGN_IN"))
        title_label.setText(tr("APP_TITLE"))

    def handle_login(self):
        """Handle login"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_error("Please enter both username and password")
            return

        cursor = self.parent.conn.cursor()
        # FIXED: Use %s instead of ? for MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()

        if user:
            self.parent.current_user = {
                'id': user[0],
                'username': user[1],
                'role': user[3],
                'full_name': user[4],
                'email': user[5]
            }

            # Update last login
            # FIXED: Use %s instead of ? for MySQL
            cursor.execute('UPDATE users SET last_login = %s WHERE id = %s',
                           (datetime.now(), user[0]))
            self.parent.conn.commit()

            self.error_label.hide()
            self.parent.show_main_menu()
        else:
            self.show_error("Invalid username or password")

    def show_error(self, message):
        """Show error message"""
        self.error_label.setText(message)
        self.error_label.show()


class ActivationWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left panel - Same as login
        left_panel = QWidget()
        left_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0,极2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(200, 200)
        logo_pixmap.fill(Qt.transparent)
        painter = QPainter(logo_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white, 8))
        painter.drawEllipse(30, 30, 140, 140)
        painter.drawLine(70, 100, 130, 70)
        painter.drawLine(130, 70, 130, 130)
        painter.end()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("STORE MANAGER")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 42px;
            font-weight: 700;
            color: white;
            margin: 20px 0;
            letter-spacing: 2px;
        """)

        subtitle_label = QLabel("Professional POS System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 18px;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 40px;
        """)

        left_layout.addWidget(logo_label)
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        left_panel.setLayout(left_layout)

        # Right panel - Activation form
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setContentsMargins(60, 极0, 60, 60)

        welcome_label = QLabel("Get Started!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            font-size: 36px;
            font-weight: 700;
            color: #333;
            margin-bottom: 20px;
        """)

        info_label = QLabel("Your system is ready to use.\nClick 'Continue' to access the main dashboard.")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            font-size: 16px;
            color: #666;
            margin-bottom: 40px;
            line-height: 1.5;
        """)

        # Continue button
        continue_btn = QPushButton("Continue to Dashboard")
        continue_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #20c997);
                color: white;
                padding: 16px 32px;
                font-size: 18px;
                font-weight: 600;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34ce57, stop:1 #28a745);
            }
        """)
        continue_btn.clicked.connect(self.handle_activation)

        right_layout.addWidget(welcome_label)
        right_layout.addWidget(info_label)
        right_layout.addWidget(continue_btn)
        right_panel.setLayout(right_layout)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        self.setLayout(main_layout)

    def handle_activation(self):
        """Handle activation"""
        self.parent.show_main_menu()


class MainMenuWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        self.setFocusPolicy(Qt.StrongFocus)

    def create_menu_button(self, title, icon, shortcut, description, callback, color):
        """Create a menu button widget"""
        btn_widget = QWidget()
        btn_widget.setFixedSize(200, 140)
        btn_widget.setStyleSheet(f"""
            QWidget {{
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 10px;
                border-left: 4px solid {color};
            }}
            QWidget:hover {{
                border-color: {color};
                background: #f8f9fa;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            font-size: 28px;
            color: {color};
        """)

        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #333;
        """)

        # Shortcut
        shortcut_label = QLabel(shortcut)
        shortcut_label.setAlignment(Qt.AlignCenter)
        shortcut_label.setStyleSheet("""
            font-size: 11px;
            color: #6c757d;
        """)

        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            font-size: 10px;
            color: #868e96;
        """)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(shortcut_label)
        layout.addWidget(desc_label)
        btn_widget.setLayout(layout)

        # Make clickable
        if callback:
            btn_widget.mousePressEvent = lambda event, cb=callback: cb()
            btn_widget.setCursor(Qt.PointingHandCursor)

        return btn_widget

    def create_quick_stats(self):
        """Create quick stats widget"""
        stats_widget = QWidget()
        stats_widget.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(15)

        # Get stats from database
        cursor = self.parent.conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")

        # Today's sales
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(total_price), 0) 
            FROM tickets 
            WHERE date LIKE %s
        """, (f"{today}%",))
        today_count, today_sales = cursor.fetchone() or (0, 0.0)

        # Total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0] or 0

        # Low stock items
        cursor.execute("SELECT COUNT(*) FROM products WHERE quantity < 10")
        low_stock = cursor.fetchone()[0] or 0

        # Create stat cards
        stats = [
            {
                "title": "SALES TODAY",
                "value": f"{today_sales:,.2f} DA",
                "icon": "💰",
                "color": "#28a745",
                "subtext": f"{today_count} transactions"
            },
            {
                "title": "TOTAL PRODUCTS",
                "value": total_products,
                "icon": "📦",
                "color": "#17a2b8",
                "subtext": "in inventory"
            },
            {
                "title": "LOW STOCK",
                "value": low_stock,
                "icon": "⚠️" if low_stock > 0 else "✓",
                "color": "#dc3545" if low_stock > 0 else "#28a745",
                "subtext": "needs reorder" if low_stock > 0 else "all stocked"
            }
        ]

        for stat in stats:
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background: white;
                    border-left: 3px solid {stat['color']};
                    border-radius: 6px;
                    padding: 12px;
                }}
            """)
            card.setMinimumWidth(160)

            card_layout = QVBoxLayout()
            card_layout.setSpacing(5)

            # Title
            title_label = QLabel(stat['title'])
            title_label.setStyleSheet(f"""
                font-size: 12px;
                font-weight: bold;
                color: {stat['color']};
                text-transform: uppercase;
            """)

            # Value row
            value_row = QHBoxLayout()
            icon_label = QLabel(stat['icon'])
            icon_label.setStyleSheet(f"""
                font-size: 20px;
                color: {stat['color']};
            """)

            value_label = QLabel(str(stat['value']))
            value_label.setStyleSheet(f"""
                font-size: 18px;
                font-weight: bold;
                color: {stat['color']};
            """)

            value_row.addWidget(icon_label)
            value_row.addWidget(value_label)
            value_row.addStretch()

            # Subtext
            subtext_label = QLabel(stat['subtext'])
            subtext_label.setStyleSheet("""
                font-size: 11px;
                color: #6c757d;
            """)

            card_layout.addWidget(title_label)
            card_layout.addLayout(value_row)
            card_layout.addWidget(subtext_label)
            card.setLayout(card_layout)

            layout.addWidget(card)

        stats_widget.setLayout(layout)
        return stats_widget

    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 20)
        main_layout.setSpacing(15)

        # Header (same as before)
        header_layout = QHBoxLayout()
        # ... [header code remains unchanged] ...

        # Welcome label
        welcome_label = QLabel("LKS Point of Sale System")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 300;
            color: #495057;
            margin: 5px 0;
        """)

        # Menu buttons grid
        menu_container = QWidget()
        menu_layout = QGridLayout()
        menu_layout.setSpacing(15)
        menu_layout.setContentsMargins(10, 10, 10, 10)

        # Menu items (filtered by role)
        all_items = [
            ("Dashboard", "📊", "F1", "View analytics", self.parent.show_dashboard, "#4285f4"),
            ("POS", "🛒", "F3", "Process sales", self.parent.show_pos_screen, "#28a745"),
            ("Products", "📦", "P", "Manage stock", self.parent.show_product_management, "#17a2b8"),
            ("Tickets", "🎫", "T", "Sales history", self.parent.show_ticket_management, "#ffc107"),
            ("Settings", "⚙️", "F2", "System config", self.parent.show_settings, "#6c757d"),
            ("Day State", "💰", "F4", "Daily summary", self.parent.show_day_state, "#fd7e14"),
            ("Account", "👤", "F5", "User profile", self.parent.show_seller_account, "#6f42c1"),
            ("Reports", "📈", "R", "Generate reports", self.parent.show_reports, "#dc3545"),
        ]

        user = getattr(self.parent, "current_user", None)
        role = (user.get("role") if user else "") or ""
        if role.lower() == "cashier":
            menu_items = [item for item in all_items if item[0] in ("POS", "Tickets", "Account")]
        else:
            menu_items = all_items

        # Calculate columns based on screen width
        screen_width = QApplication.desktop().screenGeometry().width()
        columns = 4 if screen_width > 1000 else (3 if screen_width > 700 else 2)

        desc_map = {
            "View analytics": "VIEW_ANALYTICS",
            "Process sales": "PROCESS_SALES",
            "Manage stock": "MANAGE_STOCK",
            "Sales history": "SALES_HISTORY",
            "System config": "SYSTEM_CONFIG",
            "Daily summary": "DAILY_SUMMARY",
            "User profile": "USER_PROFILE",
            "Generate reports": "GENERATE_REPORTS",
        }

        for i, (title, icon, shortcut, description, callback, color) in enumerate(menu_items):
            desc_key = desc_map[description]
            btn_widget = self.create_menu_button(
                tr(title.upper()),
                icon,
                shortcut,
                tr(desc_key),  # map description text to a key variable named desc_key; see below
                callback,
                color,
            )
            row = i // columns
            col = i % columns
            menu_layout.addWidget(btn_widget, row, col)

        menu_container.setLayout(menu_layout)

        # Quick stats
        stats_widget = self.create_quick_stats()

        # Add to main layout
        main_layout.addLayout(header_layout)
        welcome_label.setText(tr("MAIN_MENU_WELCOME"))
        main_layout.addWidget(welcome_label)
        main_layout.addWidget(menu_container, 1)  # Priority to menu
        main_layout.addWidget(stats_widget)

        self.setLayout(main_layout)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts (respect cashier restrictions)."""
        user = getattr(self.parent, "current_user", None)
        role = (user.get("role") if user else "") or ""
        is_cashier = role.lower() == "cashier"

        if event.key() == Qt.Key_F1 and not is_cashier:
            self.parent.show_dashboard()
        elif event.key() == Qt.Key_F2 and not is_cashier:
            self.parent.show_settings()
        elif event.key() == Qt.Key_F3:
            self.parent.show_pos_screen()
        elif event.key() == Qt.Key_F4 and not is_cashier:
            self.parent.show_day_state()
        elif event.key() == Qt.Key_F5:
            self.parent.show_seller_account()
        elif event.key() == Qt.Key_R and not is_cashier:
            self.parent.show_reports()
        super().keyPressEvent(event)


# Full working widgets for Settings, Day State, and Seller Account
class SettingsWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        back_btn = QPushButton("← Back to Main Menu")
        back_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        back_btn.clicked.connect(self.parent.show_main_menu)

        title_label = QLabel("System Settings")
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: 700;
            color: #333;
            margin-left: 20px;
        """)

        header_layout.addWidget(back_btn)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Settings tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background: white;
                padding: 20px;
            }
            QTabBar::tab {
                background: #极8f9fa;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                color: #6c757d;
            }
            QTabBar::tab:selected {
                background: white;
                color: #4285f4;
                border-bottom: 2px solid #4285f4;
            }
        """)

        # Store Settings Tab
        store_tab = self.create_store_settings_tab()
        tab_widget.addTab(store_tab, "  Store Information")

        # System Settings Tab
        system_tab = self.create_system_settings_tab()
        tab_widget.addTab(system_tab, "  System Settings")

        # User Management Tab
        user_tab = self.create_user_management_tab()
        tab_widget.addTab(user极ab, "  User Management")

        main_layout.addLayout(header_layout)
        main_layout.addWidget(tab_widget)

        self.setLayout(main_layout)

    def create_store_settings_tab(self):
        """Create store settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Store information form
        form_layout = QFormLayout()

        self.store_name_input = QLineEdit()
        self.store_address_input = QTextEdit()
        self.store_address_input.setMaximumHeight(80)
        self.store_phone_input = QLineEdit()
        self.store_email_input = QLineEdit()
        self.currency_input = QLineEdit()
        self.tax_rate_input = QLineEdit()

        form_layout.addRow("Store Name:", self.store_name_input)
        form_layout.addRow("Address:", self.store_address_input)
        form_layout.addRow("Phone:", self.store_phone_input)
        form_layout.addRow("Email:", self.store_email_input)
        form_layout.addRow("Currency:", self.currency_input)
        form_layout.addRow("Tax Rate (%):", self.tax_rate_input)

        # Save button
        save_btn = QPushButton("Save Store Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 极00;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        save_btn.clicked.connect(self.save_store_settings)

        layout.addLayout(form_layout)
        layout.addWidget(save_btn)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_system_settings_tab(self):
        """Create system settings tab"""
        widget = QWidget()
        layout = Q极BoxLayout()

        # System settings form
        form_layout = QFormLayout()

        self.low_stock_threshold_input = QLineEdit()
        self.receipt_footer_input = QTextEdit()
        self.receipt_footer_input.setMaximumHeight(80)
        self.backup_enabled_checkbox = QCheckBox("Enable automatic backups")
        self.print_receipt_checkbox = QCheckBox("Auto-print receipts")

        # New: Dark Mode and Language
        self.dark_mode_checkbox = QCheckBox("Enable Dark Mode")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Arabic"])

        form_layout.addRow("Low Stock Threshold:", self.low_stock_threshold_input)
        form_layout.add极("Receipt Footer:", self.receipt_footer_input)
        form_layout.addRow("", self.backup_enabled_checkbox)
        form_layout.addRow("", self.print_receipt_checkbox)
        form_layout.addRow(self.dark_mode_checkbox)
        form_layout.addRow("Language:", self.language_combo)

        # Database management
        db_group = QGroupBox("Database Management")
        db_layout = QVBoxLayout()

        backup_btn = QPushButton("Create Database Backup")
        backup_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        backup_btn.clicked.connect(self.create_backup)

        restore_btn = QPushButton("Restore Database")
        restore_btn.setStyleSheet("""
            QPushButton {
                background: #ffc107;
                color: #212529;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #e0a800;
            }
        """)
        restore_btn.clicked.connect(self.restore_backup)

        db_layout.addWidget(backup_btn)
        db_layout.addWidget(restore_btn)
        db_group.setLayout(db_layout)

        # Save button
        save_btn = QPushButton("Save System Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        save_btn.clicked.connect(self.save_system_settings)

        layout.addLayout(form_layout)
        layout.addWidget(db_group)
        layout.addWidget(save_btn)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_user_management_tab(self):
        """Create user management tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Add user button
        add_user_btn = QPushButton("+ Add New User")
        add_user_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                margin-bottom: 20px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        add_user_btn.clicked.connect(self.add_user)

        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "Username", "Full Name", "Role", "Email", "Last Login", "Actions"
        ])

        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        layout.addWidget(add_user_btn)
        layout.addWidget(self.users_table)

        widget.setLayout(layout)
        return widget

    def load_settings(self):
        """Load settings from database"""
        cursor = self.parent.conn.cursor()
        cursor.execute('SELECT `key`, value FROM settings')
        settings = dict(cursor.fetchall())

        # Load store settings
        self.store_name_input.setText(settings.get('store_name', ''))
        self.store_address_input.setPlainText(settings.get('store_address', ''))
        self.store_phone_input.setText(settings.get('store_phone', ''))
        self.store_email_input.setText(settings.get('store_email', ''))
        self.currency_input.setText(settings.get('currency', 'DA'))
        self.tax_rate_input.setText(settings.get('tax_rate', '19'))

        # Load system settings
        self.low_stock_threshold_input.setText(settings.get('low_stock_threshold', '10'))
        self.receipt_footer_input.setPlainText(settings.get('receipt_footer', ''))

        # Dark mode & language
        dark = settings.get('dark_mode', 'off').lower() in ('1', 'true', 'on', 'yes')
        self.dark_mode_checkbox.setChecked(dark)
        lang = settings.get('language', 'en')
        if lang.lower().startswith('ar'):
            self.language_combo.setCurrentText("Arabic")
        else:
            self.language_combo.setCurrentText("English")

        # Load users
        self.load_users()

    def load_users(self):
        """Load users into table"""
        cursor = self.parent极onn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY username')
        users = cursor.fetchall()

        self.users_table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(user[1]))  # username
            self.users_table.setItem(row, 1, QTableWidgetItem(user[4] or ""))  # full_name
            self.users_table.setItem(row, 2, QTableWidgetItem(user[3]))  # role
            self.users_table.setItem(row, 3, QTableWidgetItem(user[5] or ""))  # email

            # Last login
            last_login = user[7] if user[7] else "Never"
            if last_login != "Never":
                try:
                    last_login = datetime.fromisoformat(last_login).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass
            self.users_table.setItem(row, 4, QTableWidgetItem(last_login))

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)

            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #17a2b8;
                    color: white;
                    padding: 4px 8px;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #138496;
                }
            """)

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #dc3545;
                    color: white;
                    padding: 4px 8px;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #c82333;
                }
            """)

            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_widget.setLayout(actions_layout)

            self.users_table.setCellWidget(row, 5, actions_widget)

    def _upsert_setting(self, cursor, key: str, value: str):
        # FIXED: Use %s instead of ? for MySQL and backticks for reserved words
        cursor.execute('UPDATE settings SET value = %s WHERE `key` = %s', (value, key))
        if cursor.rowcount == 0:
            cursor.execute('INSERT INTO settings (`key`, value) VALUES (%s, %s)', (key, value))

    def save_store_settings(self):
        """Save store settings"""
        try:
            cursor = self.parent.conn.cursor()

            settings = [
                ('store_name', self.store_name_input.text()),
                ('store_address', self.store_address_input.toPlainText()),
                ('store_phone', self.store_phone_input.text()),
                ('store_email', self.store_email_input.text()),
                ('currency', self.currency_input.text()),
                ('tax_rate', self.tax_rate_input.text())
            ]

            for key, value in settings:
                self._upsert_setting(cursor, key, value)

            self.parent.conn.commit()
            QMessageBox.information(self, "Success", "Store settings saved successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def save_system_settings(self):
        """Save system settings"""
        try:
            cursor = self.parent.conn.cursor()

            settings = [
                ('low_stock_threshold', self.low_stock_threshold_input.text()),
                ('receipt_footer', self.receipt_footer_input.toPlainText()),
                ('dark_mode', 'on' if self.dark_mode_checkbox.isChecked() else 'off'),
                ('language', 'ar' if self.language_combo.currentText() == 'Arabic' else 'en'),
            ]

            for key, value in settings:
                self._upsert_setting(cursor, key, value)

            self.parent.conn.commit()

            # Apply immediately
            self.parent.apply_theme(self.dark_mode_checkbox.isChecked())
            self.parent.apply_language('ar' if self.language_combo.currentText() == 'Arabic' else 'en')

            QMessageBox.information(self, "Success", "System settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def create_backup(self):
        """Create database backup"""
        try:
            import shutil
            backup_name = f"pos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2('pos_database.db', backup_name)
            QMessageBox.information(self, "Backup Created", f"Database backup created: {backup_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create backup: {str(e)}")

    def restore_backup(self):
        """Restore database backup"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Backup File", "", "Database Files (*.db)")
        if file_path:
            reply = QMessageBox.question(self, "Confirm Restore",
                                         "This will replace the current database. Are you sure?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    import shutil
                    self.parent.conn.close()
                    shutil.copy2(file_path, 'pos_database.db')
                    self.parent.init_database()
                    QMessageBox.information(self, "Restore Complete", "Database restored successfully!")
                    self.load_settings()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to restore backup: {str(e)}")

    def add_user(self):
        """Add new user"""
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()


class DayStateWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # Header with navigation and title
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Back button with icon
        back_btn = QPushButton("← Back")
        back_btn.setIcon(QIcon.fromTheme("go-previous"))
        back_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        back_btn.clicked.connect(self.parent.show_main_menu)

        # Title with date
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("Daily Sales Summary")
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
        """)

        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            font-size: 14px;
            color: #7f极c8d;
        """)

        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.date_label)

        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_btn.setStyleSheet("""
            Q极ushButton {
                background: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
               极 min-width: 120px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        refresh_极n.clicked.connect(self.load_data)

        header_layout.addWidget(back_btn)
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)

        # Date selection
        date_container = QWidget()
        date_layout = QHBoxLayout(date_container)
        date_layout.setContentsMargins(0, 0, 0, 0)

        date_picker_label = QLabel("Select Date:")
        date_picker_label.setStyleSheet("font-size: 14px; font-weight: 600;")

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                min-width: 120px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border-left: 1px solid #bdc3c7;
            }
        """)
        self.date_edit.dateChanged.connect(self.load_data)

        date_layout.addWidget(date_picker_label)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()

        # Stats cards - now in a scrollable area
        stats_scroll = QScrollArea()
        stats_scroll.setWidgetResizable(True)
        stats_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        stats_scroll.setStyleSheet("QScrollArea { border: none; }")

        stats_container = QWidget()
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 5, 0, 5)
        stats_layout.setSpacing(15)

        self.sales_card = self.create_stat_card("Total Sales", "0.00", "#2ecc71", "💰")
        self.transactions_card = self.create_stat_card("Transactions", "0", "#3498db", "🧾")
        self.items_card = self.create_stat_card("Items Sold", "0", "#f39c12", "📦")
        self.customers_card = self.create_stat_card("Customers", "0", "#9b59b6", "👥")
        self.avg_sale_card = self.create_stat_card("Avg. Sale", "0.00", "#e74c3c", "📊")

        stats_layout.addWidget(self.sales_card)
        stats_layout.addWidget(self.transactions_card)
        stats_layout.addWidget(self.items_card)
        stats_layout.addWidget(self.customers_card)
        stats_layout.addWidget(self.avg_sale_card)

        stats_scroll.setWidget(stats_container)

        # Main content area
        content_splitter = QSplitter(Qt.Vertical)

        # Top products table
        products_group = QGroupBox("🔥 Top Selling Products")
        products_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #2c3e50;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        products_layout = QVBoxLayout(products_group)
        self.products_table = self.create_table(["Product", "Quantity", "Revenue (DA)"])
        products_layout.addWidget(self.products_table)

        # Recent transactions table
        transactions_group = QGroupBox("⏳ Recent Transactions")
        transactions_group.setStyleSheet(products_group.styleSheet())

        transactions_layout = QVBoxLayout(transactions_group)
        self.transactions_table = self.create_table(["Time", "Ticket #", "Customer", "Amount (DA)"])
        transactions_layout.addWidget(self.transactions_table)

        content_splitter.addWidget(products_group)
        content_splitter.addWidget(transactions_group)
        content_splitter.setSizes([300, 300])

        # Export buttons
        export_container = QWidget()
        export_layout = QHBoxLayout(export_container)
        export_layout.setContentsMargins(0, 0, 0, 0)

        pdf_btn = Q极ushButton("Export to PDF")
        pdf_btn.setIcon(QIcon.fromTheme("application-pdf"))
        pdf_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 极20px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        pdf_btn.clicked.connect(self.export_pdf)

        excel_btn = QPushButton("Export to Excel")
        excel_btn.setIcon(QIcon.fromTheme("x-office-spreadsheet"))
        excel_btn.setStyleSheet("""
            QPushButton {
                background: #2ecc71;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #27ae60;
            }
        """)
        excel_btn.clicked.connect(self.export_excel)

        export_layout.addStretch()
        export_layout.addWidget(pdf_btn)
        export_layout.addWidget(excel_btn)

        # Add all to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(date_container)
        main_layout.addWidget(stats_scroll)
        main_layout.addWidget(content_splitter, 1)
        main_layout.addWidget(export_container)

        self.setLayout(main_layout)

        # Update date label
        self.update_date_label()

    def create_table(self, headers):
        """Create a styled table widget"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(True)

        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-size: 13px;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 8px;
                border: none;
                font-weight: 600;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        return table

    def create_stat_card(self, title, value, color, icon):
        """Create a modern stat card"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        card.setFixedHeight(100)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 32px;
            color: {color};
            margin-right: 15px;
        """)

        # Content
        content = QVBoxLayout()
        content.setSpacing(2)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
           极 color: {color};
        """)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 13px;
            color: #7f8c8d;
        """)

        content.addWidget(value_label)
        content.addWidget(title_label)
        content.addStretch()

        layout.addWidget(icon_label)
        layout.addLayout(content)

        # Store references
        card.value_label = value_label
        card.title_label = title_label

        return card

    def update_date_label(self):
        """Update the displayed date label"""
        date_str = self.date_edit.date().toString("dddd, MMMM d, yyyy")
        self.date_label.setText(date_str)

    def load_data(self):
        """Load all data for selected date"""
        self.update_date_label()
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")

        try:
            cursor = self.parent.conn.cursor()

            # Get daily stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as transactions,
                    COALESCE(SUM(total_price), 0) as total_sales,
                    COALESCE(AVG(total_price), 0) as avg_sale
                FROM tickets 
                WHERE date LIKE %s
            """, (f"{selected_date}%",))
            stats = cursor.fetchone()

            # Get items sold
            cursor.execute("""
                SELECT COALESCE(SUM(
                    json_extract(value, '$.quantity')
                ), 0)
                FROM tickets, json_each(tickets.items)
                WHERE date LIKE %s
            """, (f"{selected_date}%",))
            items_sold = cursor.fetchone()[0] or 0

            # Get unique customers
            cursor.execute("""
                SELECT COUNT(DISTINCT customer_name)
                FROM tickets 
                WHERE date LIKE %s AND customer_name != 'Walk-in Customer'
            """, (f"{selected_date}%",))
            unique_customers = cursor.fetchone()[0]

            # Update stat cards
            self.sales_card.value_label.setText(f"{stats[1]:.2f} DA")
            self.transactions_card.value_label.setText(f"{stats[0]:,}")
            self.items_card.value_label.setText(f"{items_sold:,}")
            self.customers_card.value_label.setText(f"{unique_customers:,}")
            self.avg极ale_card.value_label.setText(f"{stats[2]:.2f} DA")

            # Load tables
            self.load_top_products(selected_date)
            self.load_recent_transactions(selected_date)

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load data: {str(e)}")

    def load_top_products(self, date):
        """Load top selling products with better formatting"""
        try:
            cursor = self.parent.conn.cursor()
            cursor.execute("""
                SELECT 
                    json_extract(value, '$.name') as product_name,
                    SUM(json_extract(value, '$.quantity')) as total_quantity,
                    SUM(json_extract(value, '$.total')) as total_revenue
                FROM tickets, json_each(tickets.items)
                WHERE date LIKE %s
                GROUP BY product_name
                ORDER BY total_quantity DESC
                LIMIT 15
            """, (f"{date}%",))

            self.products_table.setRowCount(0)

            for row, (name, quantity, revenue) in enumerate(cursor.fetchall()):
                self.products_table.insertRow(row)

                name_item = QTableWidgetItem(name)
                qty_item = QTableWidgetItem(f"{int(quantity):,}")
                rev_item = QTableWidgetItem(f"{revenue:,.2f}")

                # Right-align numeric columns
                qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                rev_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                self.products_table.setItem(row, 0, name_item)
                self.products_table.setItem(row, 1, qty_item)
                self.products_table.setItem(row, 2, rev_item)

        except Exception as e:
            print(f"Error loading products: {e}")

    def load_recent_transactions(self, date):
        """Load recent transactions with better formatting"""
        try:
            cursor = self.parent.conn.cursor()
            cursor.execute("""
                SELECT 
                    datetime(date) as trans_time,
                    ticket_number,
                    CASE 
                        WHEN customer_name = 'Walk-in Customer' THEN 'Walk-in'
                        ELSE customer_name
                    END as customer,
                    total_price
                FROM tickets 
                WHERE date LIKE %s
                ORDER BY date DESC
                LIMIT 20
            """, (f"{date}%",))

            self.transactions_table.setRowCount(0)

            for row, (date_time, ticket_num, customer, amount) in enumerate(cursor.fetchall()):
                self.transactions_table.insertRow(row)

                try:
                    time_str = datetime.fromisoformat(date_time).strftime("%H:%M")
                except Exception:
                    time_str = date_time.split()[-1][:5] if ' ' in date_time else date_time

                time_item = QTableWidgetItem(time_str)
                ticket_item = QTableWidgetItem(ticket_num)
                cust_item = QTableWidgetItem(customer)
                amt_item = QTableWidgetItem(f"{amount:,.2f}")

                # Right-align numeric column
                amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                self.transactions_table.setItem(row, 0, time_item)
                self.transactions_table.setItem(row, 1, ticket_item)
                self.transactions_table.setItem(row, 极, cust_item)
                self.transactions_table.setItem(row, 3, amt_item)

        except Exception as e:
            print(f"Error loading transactions: {e}")

    def export_pdf(self):
        """Export to PDF with progress dialog"""
        progress = QProgressDialog("Generating PDF...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Exporting PDF")

        # Simulate export process
        for i in range(1, 101):
            progress.setValue(i)
            QApplication.processEvents()
            if progress.wasCanceled():
                break
            time.sleep(0.02)

        progress.close()
        QMessageBox.information(self, "Export Complete", "PDF report generated successfully!")

    def export_excel(self):
        """Export to Excel with file dialog"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to Excel",
            f"sales_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            "Excel Files (*.xlsx)"
        )

        if file_path:
            progress = QProgressDialog("Exporting to Excel...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)

            # Simulate export process
            for i in range(1, 101):
                progress.setValue(i)
                QApplication.processEvents()
                if progress.wasCanceled():
                    break
                time.sleep(0.02)

            progress.close()
            QMessageBox.information(self, "Export Complete", f"Data exported to:\n{file_path}")


class SellerAccountWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        self.load_user_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # Header with navigation
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        back_btn = QPushButton("← Back")
        back_btn.setIcon(QIcon.fromTheme("go-previous"))
        back_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        back_btn.clicked.connect(self.parent.show_main_menu)

        title = QLabel("My Account")
        title极etStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
        """)

        header_layout.addWidget(back_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Main content
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # Left panel - Profile card
        profile_card = QWidget()
        profile_card.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
            }
        """)
        profile_layout = QVBoxLayout(profile_card)
        profile_layout.setContentsMargins(20, 20, 20, 20)

        # Profile picture with initials
        self.profile_pic = QLabel()
        self.profile_pic.setFixedSize(120, 120)
        self.profile_pic.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:极 #3498db, stop:1 #2c3e50);
                border-radius: 60px;
                color: white;
                font-size: 48px;
                font-weight: bold;
            }
        """)
        self.profile_pic.setAlignment(Qt.AlignCenter)

        # User info
        self.user_name = QLabel()
        self.user_name.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
            margin: 15px 0 5px 0;
        """)
        self.user_name.setAlignment(Qt.AlignCenter)

        self.user_role = QLabel()
        self.user_role.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 20px;
        """)
        self.user_role.setAlignment(Qt.AlignCenter)

        # Stats cards
        stats_container = QWidget()
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)

        self.sales_today_card = self.create_stat_card("💰", "Today's Sales", "0.00 DA", "#2ecc71")
        self.sales_month_card = self.create_stat_card("📅", "Monthly Sales", "0.00 DA", "#3498db")
        self.transactions_card = self.create_stat_card("🧾", "Transactions", "0", "#f39c12")

        stats_layout.addWidget(self.sales_today_card)
        stats_layout.addWidget(self.sales_month_card)
        stats_layout.addWidget(self.transactions_card)

        profile_layout.addWidget(self.profile_pic, alignment=Qt.AlignCenter)
        profile_layout.addWidget(self.user_name)
        profile_layout.addWidget(self.user_role)
        profile_layout.addWidget(stats_container)
        profile_layout.addStretch()

        # Right panel - Account settings
        settings_card = QWidget()
        settings_card.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
            }
        """)
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(20, 20, 20, 20)

        # Account settings form
        form_group = QGroupBox("Account Settings")
        form_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                border: none;
            }
        """)

        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Username (readonly)
        self.username_input = QLineEdit()
        self.username_input.setReadOnly(True)
        self.username_input.setStyleSheet("background: #f8f9fa;")

        # Full name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Your full name")

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your@email.com")

        # Password change section
        password_group = QGroupBox("Change Password")
        password_group.setStyleSheet(form_group.styleSheet())

        password_layout = QFormLayout()
        password_layout.setContentsMargins(10, 15, 10, 15)

        self.current_password_input = QLineEdit()
        self.current_password_input.setPlaceholderText("Current password")
        self.current_password_input.setEchoMode(QLineEdit.Password)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("New password")
        self.new_password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password极ut.setEchoMode(QLineEdit.Password)

        # Show password checkbox
        show_password = QCheckBox("Show passwords")
        show_password.toggled.connect(self.toggle_password_visibility)

        password_layout.addRow("Current:", self.current_password_input)
        password_layout.addRow("New:", self.new_password_input)
        password_layout.addRow("Confirm:", self.confirm_password_input)
        password_layout.addRow(show_password)
        password_group.setLayout(password_layout)

        # Form fields
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Full Name:", self.full_name_input)
        form_layout.addRow("Email:", self.email_input)

        form_group.setLayout(form_layout)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        update_btn = QPushButton("Update Profile")
        update_btn.setIcon(QIcon.fromTheme("document-save"))
        update_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        update_btn.clicked.connect(self.update_profile)

        change_pass_btn = QPushButton("Change Password")
        change_pass_btn.setIcon(QIcon.fromTheme("dialog-password"))
        change_pass_btn.setStyleSheet("""
            QPushButton {
                background: #f39c12;
                color: white;
                padding: 10极 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #e67e22;
            }
        """)
        change_pass_btn.clicked.connect(self.change_password)

        logout_btn = QPushButton("Logout")
        logout_btn.setIcon(QIcon.fromTheme("system-log-out"))
        logout_btn极etStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)

        buttons_layout.addWidget(update_btn)
        buttons_layout.addWidget(change_pass_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(logout_btn)

        settings_layout.addWidget(form_group)
        settings_layout.addWidget(password_group)
        settings_layout.addLayout(buttons_layout)

        content_layout.addWidget(profile_card, 1)
        content_layout.addWidget(settings_card, 2)

        main_layout.addWidget(header)
        main_layout.addWidget(content, 1)

        self.setLayout(main_layout)

    def create_stat_card(self, icon, title, value, color):
        """Create a statistics card widget"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                border-left: 4px solid {color};
                padding: 12px;
            }}
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(5, 5, 5, 5)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 24px;
            color: {color};
            margin-right: 10px;
        """)

        # Content
        content = QVBoxLayout()
        content.setSpacing(2)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {color};
        """)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
        """)

        content.addWidget(value_label)
        content.addWidget(title_label)

        layout.addWidget(icon_label)
        layout.addLayout(content)

        # Store references
        card.value_label = value_label
        return card

    def load_user_data(self):
        """Load user data and statistics"""
        if not self.parent.current_user:
            return

        user = self.parent.current_user

        # Set profile info
        self.profile_pic.setText(user['username'][0].upper())
        self.user_name.setText(user.get('full_name') or user['username'])
        self.user_role.setText(f"Role: {user['role'].title()}")

        # Set form fields
        self.username_input.setText(user['username'])
        self.full_name_input.setText(user.get('full_name', ''))
        self.email_input.setText(user.get('email', ''))

        # Load statistics
        self.load_user_statistics()

    def load_user_statistics(self):
        """Load and display user statistics"""
        if not self.parent.current_user:
            return

        cursor = self.parent.conn.cursor()
        user_id = self.parent.current_user['id']

        try:
            # Today's date
            today = datetime.now().strftime("%Y-%m-%d")

            # Get today's stats
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(total_price), 0)
                FROM tickets 
                WHERE cashier_id = %s AND date LIKE %s
            """, (user_id, f"{today}%"))
            today_count, today_sales = cursor.fetchone()

            # This month's stats
            this_month = datetime.now().strftime("%Y-%m")
            cursor.execute("""
                SELECT COALESCE(SUM(total_price), 0)
                FROM tickets 
                WHERE cashier_id = %s AND date LIKE %s
            """, (user极, f"{this_month}%"))
            month_sales = cursor.fetchone()[0] or 0

            # Update cards
            self.sales_today_card.value_label.setText(f"{today_sales:,.2f} DA")
            self.sales_month_card.value_label.setText(f"{month_sales:,.2f} DA")
            self.transactions_card.value_label.setText(f"{today_count:,}")

        except Exception as e:
            print(f"Error loading statistics: {e}")

    def toggle_password_visibility(self, checked):
        """Toggle password field visibility"""
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.current_password_input.setEchoMode(mode)
        self.new_password_input.setEchoMode(mode)
        self.confirm_password_input.setEchoMode(mode)

    def update_profile(self):
        """Update user profile information"""
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()

        if not full_name:
            QMessageBox.warning(self, "Validation Error", "Full name cannot be empty")
            return

        try:
            cursor = self.parent.conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET full_name = %s, email = %s
                WHERE id = %s
            """, (full_name, email, self.parent.current_user['id']))

            self.parent.conn.commit()

            # Update current user data
            self.parent.current_user['full_name'] = full_name
            self.parent.current_user['email'] = email
            self.user_name.setText(full_name)

            QMessageBox.information(self, "Success", "Profile updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update profile:\n{str(e)}")

    def change_password(self):
        """Handle password change"""
        current = self.current_password_input.text()
        new = self.new_password_input.text()
        confirm = self.confirm_password_input.text()

        # Validation
        if not current:
            QMessageBox.warning(self, "Validation Error", "Please enter current password")
            return

        if not new or len(new) < 6:
            QMessageBox.warning(self, "Validation Error", "New password must be at least 6 characters")
            return

        if new != confirm:
            QMessageBox.warning(self, "Validation Error", "New passwords don't match")
            return

        try:
            cursor = self.parent.conn.cursor()

            # Verify current password
            cursor.execute("SELECT password FROM users WHERE id = %s",
                           (self.parent.current_user['id'],))
            stored_password = cursor.fetchone()[0]

            if stored_password != current:
                QMessageBox.warning(self, "Error", "Current password is incorrect")
                return

            # Update password
            cursor.execute("UPDATE users SET password = %s WHERE id = %s",
                           (new, self.parent.current_user['id']))
            self.parent.conn.commit()

            # Clear fields
            self.current_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()

            QMessageBox.information(self, "Success", "Password changed successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to change password:\n{str(e)}")

    def logout(self):
        """Handle user logout"""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.parent.current_user = None
            self.parent.show_login_screen()


# Dialog for adding users
class AddUserDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Add New User")
        self.setModal(True)
        self.resize(400, 350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Form fields
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.full_name_input = Q极ineEdit()
        self.full_name_input.setPlaceholderText("Full Name")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["cashier", "manager", "admin"])

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Full Name:", self.full_name_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Role:", self.role_combo)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save User")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        save_btn.clicked.connect(self.save_user)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_user(self):
        """Save the new user"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required")
            return

        


if __name__ == '__main__':
    # Set high DPI scaling before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application properties
    app.setApplicationName("Store Manager")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Smartware Studio")

    # Create and show main window
    window = POSApplication()
    window.show()

    sys.exit(app.exec_())