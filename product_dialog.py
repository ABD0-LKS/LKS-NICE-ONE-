from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import mysql.connector
from mysql_config import get_mysql_connection

class ProductDialog(QDialog):
    def __init__(self, parent, title, product=None):
        super().__init__(parent)
        self.parent = parent
        self.product = product
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(500, 600)
        self.init_ui()
        
        if product:
            self.load_product_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form fields
        form_layout = QFormLayout()
        
        self.code_bar_input = QLineEdit()
        self.code_bar_input.setPlaceholderText("Code bar")
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")
        
        self.price_sell_input = QLineEdit()
        self.price_sell_input.setPlaceholderText("Price Sell")
        
        self.price_buy_input = QLineEdit()
        self.price_buy_input.setPlaceholderText("Price Buy")
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Quantity")
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["General", "Electronics", "Beauty", "Clothing", "Food"])
        
        form_layout.addRow("Code bar:", self.code_bar_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Price Sell:", self.price_sell_input)
        form_layout.addRow("Price Buy:", self.price_buy_input)
        form_layout.addRow("Quantity:", self.quantity_input)
        form_layout.addRow("Category:", self.category_combo)
        
        # Benefit calculation
        self.benefit_label = QLabel("Benefit per piece: 0.00 DA")
        self.benefit_label.setStyleSheet("color: #2196f3; font-weight: bold; margin: 10px;")
        
        self.total_benefit_label = QLabel("Total benefit: 0.00 DA")
        self.total_benefit_label.setStyleSheet("color: #2196f3; font-weight: bold; margin: 10px;")
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #666; color: white; padding: 10px 20px; border-radius: 8px;")
        close_btn.clicked.connect(self.reject)
        
        done_btn = QPushButton("Done")
        done_btn.setStyleSheet("background-color: #4285f4; color: white; padding: 10px 20px; border-radius: 8px;")
        done_btn.clicked.connect(self.save_product)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        buttons_layout.addWidget(done_btn)
        
        # Connect inputs to benefit calculation
        self.price_sell_input.textChanged.connect(self.calculate_benefit)
        self.price_buy_input.textChanged.connect(self.calculate_benefit)
        self.quantity_input.textChanged.connect(self.calculate_benefit)
        
        layout.addLayout(form_layout)
        layout.addWidget(self.benefit_label)
        layout.addWidget(self.total_benefit_label)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def load_product_data(self):
        if self.product:
            self.code_bar_input.setText(self.product[2] or "")
            self.name_input.setText(self.product[1])
            self.price_buy_input.setText(str(self.product[3]))
            self.price_sell_input.setText(str(self.product[4]))
            self.quantity_input.setText(str(self.product[5]))
            
            # Set category
            category_index = self.category_combo.findText(self.product[6] or "General")
            if category_index >= 0:
                self.category_combo.setCurrentIndex(category_index)
            
            self.calculate_benefit()
    
    def calculate_benefit(self):
        try:
            price_sell = float(self.price_sell_input.text() or 0)
            price_buy = float(self.price_buy_input.text() or 0)
            quantity = int(self.quantity_input.text() or 0)
            
            benefit_per_piece = price_sell - price_buy
            total_benefit = benefit_per_piece * quantity
            
            self.benefit_label.setText(f"Benefit per piece: {benefit_per_piece:.2f} DA")
            self.total_benefit_label.setText(f"Total benefit: {total_benefit:.2f} DA")
        except ValueError:
            self.benefit_label.setText("Benefit per piece: 0.00 DA")
            self.total_benefit_label.setText("Total benefit: 0.00 DA")
    
    def save_product(self):
        try:
            name = self.name_input.text().strip()
            code_bar = self.code_bar_input.text().strip()
            price_buy = float(self.price_buy_input.text() or 0)
            price_sell = float(self.price_sell_input.text() or 0)
            quantity = int(self.quantity_input.text() or 0)
            category = self.category_combo.currentText()
            
            if not name:
                QMessageBox.warning(self, "Erreur", "Le nom du produit est requis!")
                return
            
            conn = get_mysql_connection()
            cursor = conn.cursor()
            
            if self.product:  # Edit existing product
                cursor.execute('''
                    UPDATE products 
                    SET name=%s, code_bar=%s, price_buy=%s, price_sell=%s, quantity=%s, category=%s
                    WHERE id=%s
                ''', (name, code_bar, price_buy, price_sell, quantity, category, self.product[0]))
            else:  # Add new product
                cursor.execute('''
                    INSERT INTO products (name, code_bar, price_buy, price_sell, quantity, category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (name, code_bar, price_buy, price_sell, quantity, category))
            
            conn.commit()
            cursor.close()
            conn.close()
            self.accept()
            
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs numériques valides!")
        except mysql.connector.IntegrityError:
            QMessageBox.warning(self, "Erreur", "Ce code-barres existe déjà!")
