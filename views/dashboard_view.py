from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class DashboardView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
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
        back_btn.clicked.connect(self.controller.show_main_menu)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        
        # Sidebar and main content
        main_layout = QHBoxLayout()
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Main content
        content = self.create_content()
        main_layout.addWidget(content)
        
        layout.addLayout(header_layout)
        layout.addLayout(main_layout)
        
        self.setLayout(layout)
    
    def create_sidebar(self):
        """Create sidebar navigation"""
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
        
        return sidebar_widget
    
    def create_content(self):
        """Create main dashboard content"""
        content_widget = QWidget()
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
        
        content_widget.setLayout(content_layout)
        return content_widget
    
    def create_kpi_card(self, title, value, color, icon):
        """Create KPI card"""
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
        """Create simple chart"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e0e0e0;")
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 15px; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Simple bar chart
        chart_widget = QWidget()
        chart_widget.setFixedHeight(200)
        chart_layout = QVBoxLayout()
        
        for i, (label, value) in enumerate(zip(labels, data)):
            bar_layout = QHBoxLayout()
            
            label_widget = QLabel(label)
            label_widget.setFixedWidth(80)
            label_widget.setStyleSheet("font-size: 12px; color: #666;")
            
            bar_widget = QWidget()
            bar_width = int(value * 50)
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
