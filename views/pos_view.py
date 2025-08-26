from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime

class POSView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
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
        
        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Main content
        content_layout = QHBoxLayout()
        
        # Left - Product buttons
        left_panel = self.create_product_panel()
        content_layout.addWidget(left_panel, 2)
        
        # Center - Transaction area
        center_panel = self.create_transaction_panel()
        content_layout.addWidget(center_panel, 3)
        
        # Right - Control buttons
        right_panel = self.create_control_panel()
        content_layout.addWidget(right_panel, 2)
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
    
    def create_top_bar(self):
        """Create top action bar"""
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
            if text == "Returner Admin":
                btn.clicked.connect(self.controller.show_main_menu)
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
        """Create product buttons panel"""
        widget = QWidget()
        self.product_layout = QGridLayout()
        self.product_layout.setSpacing(5)
        widget.setLayout(self.product_layout)
        return widget
    
    def create_transaction_panel(self):
        """Create transaction panel"""
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
        """Create control buttons panel"""
        widget = QWidget()
        layout = QGridLayout()
        layout.setSpacing(5)
        
        # Control buttons
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
        """Load products from database"""
        products = self.controller.product_model.get_all_products()
        
        row, col = 0, 0
        for product in products[:12]:  # Limit for grid
            btn = QPushButton(product['name'])
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
            if col >= 2:  # 2 columns
                col = 0
                row += 1
    
    def add_to_cart(self, product):
        """Add product to cart"""
        # Check if product already in cart
        for item in self.cart_items:
            if item['id'] == product['id']:
                item['quantity'] += 1
                break
        else:
            # Add new item
            self.cart_items.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price_sell'],
                'quantity': 1,
                'stock': product['quantity']
            })
        
        self.update_transaction_table()
        self.update_total()
    
    def update_transaction_table(self):
        """Update transaction table"""
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
        """Update clock display"""
        now = datetime.now()
        self.date_label.setText(now.strftime("%d/%m/%Y"))
        self.time_label.setText(now.strftime("%H:%M:%S"))
