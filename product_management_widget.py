import sys
from datetime import datetime

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QDialog, QFormLayout, QMessageBox, QAbstractItemView)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import mysql.connector
from mysql_config import get_mysql_connection

class ProductManagementWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
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
                font-size: 14px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        back_btn.clicked.connect(self.parent.show_main_menu)
        
        title_label = QLabel("Product Management")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #333;
            margin-left: 20px;
        """)
        
        # Action buttons
        add_btn = QPushButton("+ Add Product")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        add_btn.clicked.connect(self.add_product)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #4285f4;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #3367d6;
            }
        """)
        refresh_btn.clicked.connect(self.load_products)
        
        header_layout.addWidget(back_btn)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        header_layout.addWidget(refresh_btn)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #495057;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #4285f4;
            }
        """)
        self.search_input.textChanged.connect(self.filter_products)
        
        category_label = QLabel("Category:")
        category_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #495057; margin-left: 20px;")
        
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
                background: white;
                min-width: 150px;
            }
            QComboBox:focus {
                border-color: #4285f4;
            }
        """)
        self.category_combo.currentTextChanged.connect(self.filter_products)
        
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(category_label)
        filter_layout.addWidget(self.category_combo)
        filter_layout.addStretch()
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(8)
        self.products_table.setHorizontalHeaderLabels([
            "Name", "Barcode", "Category", "Buy Price", "Sell Price", "Stock", "Status", "Actions"
        ])
        
        # Set column widths
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #f1f3f4;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f8f9fa;
            }
            QTableWidget::item:selected {
                background: #e3f2fd;
                color: #1976d2;
            }
            QTableWidget::item:alternate {
                background: #f8f9fa;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 12px 8px;
                border: none;
                font-weight: 600;
                color: #495057;
            }
        """)
        
        main_layout.addLayout(header_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.products_table)
        
        self.setLayout(main_layout)
    
    def load_categories(self):
        """Load categories into combo box"""
        self.category_combo.clear()
        self.category_combo.addItem("All Categories")
        
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category')
        categories = cursor.fetchall()
        
        for category in categories:
            if category[0]:
                self.category_combo.addItem(category[0])
        
        cursor.close()
        conn.close()
    
    def load_products(self):
        """Load products into table"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY name')
        products = cursor.fetchall()
        
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Name
            name_item = QTableWidgetItem(product[1])
            self.products_table.setItem(row, 0, name_item)
            
            # Barcode
            barcode_item = QTableWidgetItem(product[2] or "")
            self.products_table.setItem(row, 1, barcode_item)
            
            # Category
            category_item = QTableWidgetItem(product[6] or "General")
            self.products_table.setItem(row, 2, category_item)
            
            # Buy Price
            buy_price_item = QTableWidgetItem(f"{product[3]:.2f}")
            buy_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 3, buy_price_item)
            
            # Sell Price
            sell_price_item = QTableWidgetItem(f"{product[4]:.2f}")
            sell_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 4, sell_price_item)
            
            # Stock
            stock_item = QTableWidgetItem(str(product[5]))
            stock_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code stock levels
            if product[5] <= 0:
                stock_item.setBackground(QColor(248, 215, 218))
                stock_item.setForeground(QColor(220, 53, 69))
            elif product[5] < 10:
                stock_item.setBackground(QColor(255, 243, 205))
                stock_item.setForeground(QColor(255, 193, 7))
            else:
                stock_item.setBackground(QColor(212, 237, 218))
                stock_item.setForeground(QColor(40, 167, 69))
            
            self.products_table.setItem(row, 5, stock_item)
            
            # Status
            if product[5] <= 0:
                status = "Out of Stock"
                status_color = QColor(220, 53, 69)
            elif product[5] < 10:
                status = "Low Stock"
                status_color = QColor(255, 193, 7)
            else:
                status = "In Stock"
                status_color = QColor(40, 167, 69)
            
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(status_color)
            self.products_table.setItem(row, 6, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #17a2b8;
                    color: white;
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #138496;
                }
            """)
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #dc3545;
                    color: white;
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #c82333;
                }
            """)
            delete_btn.clicked.connect(lambda checked, p=product: self.delete_product(p))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_widget.setLayout(actions_layout)
            
            self.products_table.setCellWidget(row, 7, actions_widget)
        
        cursor.close()
        conn.close()
        
        # Load categories after loading products
        self.load_categories()
    
    def filter_products(self):
        """Filter products based on search and category"""
        search_term = self.search_input.text().lower()
        selected_category = self.category_combo.currentText()
        
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        if selected_category == "All Categories":
            if search_term:
                cursor.execute('''
                    SELECT * FROM products 
                    WHERE LOWER(name) LIKE %s OR LOWER(code_bar) LIKE %s OR LOWER(category) LIKE %s
                    ORDER BY name
                ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute('SELECT * FROM products ORDER BY name')
        else:
            if search_term:
                cursor.execute('''
                    SELECT * FROM products 
                    WHERE category = %s AND (LOWER(name) LIKE %s OR LOWER(code_bar) LIKE %s)
                    ORDER BY name
                ''', (selected_category, f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute('SELECT * FROM products WHERE category = %s ORDER BY name', (selected_category,))
        
        products = cursor.fetchall()
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Name
            name_item = QTableWidgetItem(product[1])
            self.products_table.setItem(row, 0, name_item)
            
            # Barcode
            barcode_item = QTableWidgetItem(product[2] or "")
            self.products_table.setItem(row, 1, barcode_item)
            
            # Category
            category_item = QTableWidgetItem(product[6] or "General")
            self.products_table.setItem(row, 2, category_item)
            
            # Buy Price
            buy_price_item = QTableWidgetItem(f"{product[3]:.2f}")
            buy_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 3, buy_price_item)
            
            # Sell Price
            sell_price_item = QTableWidgetItem(f"{product[4]:.2f}")
            sell_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 4, sell_price_item)
            
            # Stock
            stock_item = QTableWidgetItem(str(product[5]))
            stock_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code stock levels
            if product[5] <= 0:
                stock_item.setBackground(QColor(248, 215, 218))
                stock_item.setForeground(QColor(220, 53, 69))
            elif product[5] < 10:
                stock_item.setBackground(QColor(255, 243, 205))
                stock_item.setForeground(QColor(255, 193, 7))
            else:
                stock_item.setBackground(QColor(212, 237, 218))
                stock_item.setForeground(QColor(40, 167, 69))
            
            self.products_table.setItem(row, 5, stock_item)
            
            # Status
            if product[5] <= 0:
                status = "Out of Stock"
                status_color = QColor(220, 53, 69)
            elif product[5] < 10:
                status = "Low Stock"
                status_color = QColor(255, 193, 7)
            else:
                status = "In Stock"
                status_color = QColor(40, 167, 69)
            
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(status_color)
            self.products_table.setItem(row, 6, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #17a2b8;
                    color: white;
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #138496;
                }
            """)
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #dc3545;
                    color: white;
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #c82333;
                }
            """)
            delete_btn.clicked.connect(lambda checked, p=product: self.delete_product(p))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_widget.setLayout(actions_layout)
            
            self.products_table.setCellWidget(row, 7, actions_widget)
        
        cursor.close()
        conn.close()
    
    def add_product(self):
        """Add new product"""
        dialog = ProductDialog(self, None)
        if dialog.exec_() == QDialog.Accepted:
            self.load_products()
    
    def edit_product(self, product):
        """Edit existing product"""
        dialog = ProductDialog(self, product)
        if dialog.exec_() == QDialog.Accepted:
            self.load_products()
    
    def delete_product(self, product):
        """Delete product"""
        reply = QMessageBox.question(self, "Delete Product", 
                                   f"Are you sure you want to delete '{product[1]}'?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM products WHERE id = %s', (product[0],))
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, "Success", "Product deleted successfully!")
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")

class ProductDialog(QDialog):
    def __init__(self, parent, product=None):
        super().__init__(parent)
        self.parent = parent
        self.product = product
        self.setWindowTitle("Edit Product" if product else "Add Product")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()
        
        if product:
            self.load_product_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form fields
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product name")
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Barcode (optional)")
        
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Category")
        
        self.buy_price_input = QLineEdit()
        self.buy_price_input.setPlaceholderText("0.00")
        
        self.sell_price_input = QLineEdit()
        self.sell_price_input.setPlaceholderText("0.00")
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("0")
        
        form_layout.addRow("Name *:", self.name_input)
        form_layout.addRow("Barcode:", self.barcode_input)
        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("Buy Price:", self.buy_price_input)
        form_layout.addRow("Sell Price *:", self.sell_price_input)
        form_layout.addRow("Quantity:", self.quantity_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save Product")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        save_btn.clicked.connect(self.save_product)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_product_data(self):
        """Load product data for editing"""
        if self.product:
            self.name_input.setText(self.product[1])
            self.barcode_input.setText(self.product[2] or "")
            self.category_input.setText(self.product[6] or "")
            self.buy_price_input.setText(str(self.product[3]))
            self.sell_price_input.setText(str(self.product[4]))
            self.quantity_input.setText(str(self.product[5]))
    
    def save_product(self):
        """Save the product"""
        name = self.name_input.text().strip()
        sell_price_text = self.sell_price_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "Product name is required")
            return
        
        if not sell_price_text:
            QMessageBox.warning(self, "Error", "Sell price is required")
            return
        
        try:
            buy_price = float(self.buy_price_input.text() or 0)
            sell_price = float(sell_price_text)
            quantity = int(self.quantity_input.text() or 0)
            
            conn = get_mysql_connection()
            cursor = conn.cursor()
            
            if self.product:  # Edit existing product
                cursor.execute('''
                    UPDATE products 
                    SET name = %s, code_bar = %s, price_buy = %s, price_sell = %s, 
                        quantity = %s, category = %s
                    WHERE id = %s
                ''', (name, self.barcode_input.text().strip(), buy_price, sell_price, 
                      quantity, self.category_input.text().strip(), self.product[0]))
                message = "Product updated successfully!"
            else:  # Add new product
                cursor.execute('''
                    INSERT INTO products (name, code_bar, price_buy, price_sell, quantity, category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (name, self.barcode_input.text().strip(), buy_price, sell_price, 
                      quantity, self.category_input.text().strip()))
                message = "Product added successfully!"
            
            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Success", message)
            self.accept()
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values for prices and quantity")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")
