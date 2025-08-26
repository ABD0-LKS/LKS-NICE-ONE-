from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MainMenuView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
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
        
        # Create menu buttons
        buttons = [
            ("Dashboard(F1)", "📊", self.controller.show_dashboard),
            ("Settings (F2)", "⚙️", None),
            ("Direct sell (f3)", "🏪", self.controller.show_pos),
            ("Day State (F4)", "💰", None),
            ("Seller Account (F5)", "👤", None)
        ]
        
        for i, (text, icon, callback) in enumerate(buttons):
            btn_widget = self.create_menu_button(text, icon, callback)
            
            row = i // 3
            col = i % 3
            menu_layout.addWidget(btn_widget, row, col)
        
        menu_widget.setLayout(menu_layout)
        
        layout.addLayout(header_layout)
        layout.addWidget(welcome_label)
        layout.addWidget(menu_widget, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def create_menu_button(self, text, icon, callback):
        """Create a menu button widget"""
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
        
        return btn_widget
