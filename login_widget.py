from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class LoginWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left side - Logo
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
        
        # Form
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
        self.password_input.setText("admin")
        self.password_input.setStyleSheet("font-size: 16px; padding: 15px;")
        
        # Error message
        self.error_label = QLabel("Admin info was incorrect")
        self.error_label.setStyleSheet("color: #ea4335; font-size: 14px; margin: 10px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        
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
        
        # Enter key support
        self.password_input.returnPressed.connect(self.handle_login)
        
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
        footer_label = QLabel("© 2025 All rights reserved By LAKAS ")
        footer_label.setStyleSheet("color: #666; font-size: 12px; margin: 20px;")
        right_layout.addWidget(footer_label)
        
        right_widget.setLayout(right_layout)
        
        layout.addWidget(left_widget, 1)
        layout.addWidget(right_widget, 1)
        self.setLayout(layout)
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        cursor = self.parent.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        
        if user:
            self.error_label.hide()
            self.parent.show_activation_screen()
        else:
            self.error_label.show()
