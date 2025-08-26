from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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
        key_label = QLabel("Activation key :")
        key_label.setStyleSheet("font-size: 16px; margin-bottom: 5px;")
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Activation Key")
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
        
        # Enter key support
        self.key_input.returnPressed.connect(self.handle_activation)
        
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
        """Handle activation"""
        # For demo, accept any key
        self.parent.show_main_menu()
