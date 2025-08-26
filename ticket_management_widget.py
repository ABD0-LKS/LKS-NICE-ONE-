import sys
from datetime import datetime

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QDialog, QFormLayout, QMessageBox, QAbstractItemView,
                             QTextEdit, QDateEdit)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QDate
import json

class TicketManagementWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_tickets()
    
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
        
        title_label = QLabel("Ticket Management")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #333;
            margin-left: 20px;
        """)
        
        # Action buttons
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
        refresh_btn.clicked.connect(self.load_tickets)
        
        export_btn = QPushButton("📄 Export")
        export_btn.setStyleSheet("""
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
        
        header_layout.addWidget(back_btn)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(export_btn)
        header_layout.addWidget(refresh_btn)
        
        # Filter layout
        filter_layout = QHBoxLayout()
        
        # Date filter
        date_label = QLabel("Date:")
        date_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #495057;")
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }
        """)
        
        to_label = QLabel("to")
        to_label.setStyleSheet("font-size: 14px; color: #495057;")
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }
        """)
        
        filter_btn = QPushButton("Filter")
        filter_btn.setStyleSheet("""
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
        filter_btn.clicked.connect(self.filter_tickets)
        
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(to_label)
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(filter_btn)
        filter_layout.addStretch()
        
        # Tickets table
        self.tickets_table = QTableWidget()
        self.tickets_table.setColumnCount(6)
        self.tickets_table.setHorizontalHeaderLabels([
            "Ticket #", "Date", "Total", "Discount", "Items", "Actions"
        ])
        
        # Set column widths
        header = self.tickets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.tickets_table.setAlternatingRowColors(True)
        self.tickets_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tickets_table.setStyleSheet("""
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
        main_layout.addWidget(self.tickets_table)
        
        self.setLayout(main_layout)
    
    def load_tickets(self):
        """Load tickets into table"""
        cursor = self.parent.conn.cursor()
        cursor.execute('SELECT * FROM tickets ORDER BY date DESC')
        tickets = cursor.fetchall()
        
        self.tickets_table.setRowCount(len(tickets))
        
        for row, ticket in enumerate(tickets):
            # Ticket number
            number_item = QTableWidgetItem(str(ticket[1]))
            number_item.setTextAlignment(Qt.AlignCenter)
            self.tickets_table.setItem(row, 0, number_item)
            
            # Date
            date_item = QTableWidgetItem(ticket[2])
            self.tickets_table.setItem(row, 1, date_item)
            
            # Total
            total_item = QTableWidgetItem(f"{ticket[3]:.2f} DA")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tickets_table.setItem(row, 2, total_item)
            
            # Discount
            discount_item = QTableWidgetItem(f"{ticket[4]:.2f} DA")
            discount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tickets_table.setItem(row, 3, discount_item)
            
            # Items summary
            try:
                items = json.loads(ticket[5]) if ticket[5] else []
                items_summary = f"{len(items)} items"
                if items:
                    first_item = items[0]['name'] if 'name' in items[0] else 'Item'
                    if len(items) > 1:
                        items_summary = f"{first_item} + {len(items)-1} more"
                    else:
                        items_summary = first_item
            except:
                items_summary = "No items"
            
            items_item = QTableWidgetItem(items_summary)
            self.tickets_table.setItem(row, 4, items_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            view_btn = QPushButton("View")
            view_btn.setStyleSheet("""
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
            view_btn.clicked.connect(lambda checked, t=ticket: self.view_ticket(t))
            
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
            delete_btn.clicked.connect(lambda checked, t=ticket: self.delete_ticket(t))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(delete_btn)
            actions_widget.setLayout(actions_layout)
            
            self.tickets_table.setCellWidget(row, 5, actions_widget)
    
    def filter_tickets(self):
        """Filter tickets by date range"""
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        
        cursor = self.parent.conn.cursor()
        cursor.execute('''
            SELECT * FROM tickets 
            WHERE date BETWEEN ? AND ? 
            ORDER BY date DESC
        ''', (date_from, date_to))
        
        tickets = cursor.fetchall()
        self.tickets_table.setRowCount(len(tickets))
        
        for row, ticket in enumerate(tickets):
            # Same logic as load_tickets but for filtered results
            # Ticket number
            number_item = QTableWidgetItem(str(ticket[1]))
            number_item.setTextAlignment(Qt.AlignCenter)
            self.tickets_table.setItem(row, 0, number_item)
            
            # Date
            date_item = QTableWidgetItem(ticket[2])
            self.tickets_table.setItem(row, 1, date_item)
            
            # Total
            total_item = QTableWidgetItem(f"{ticket[3]:.2f} DA")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tickets_table.setItem(row, 2, total_item)
            
            # Discount
            discount_item = QTableWidgetItem(f"{ticket[4]:.2f} DA")
            discount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tickets_table.setItem(row, 3, discount_item)
            
            # Items summary
            try:
                items = json.loads(ticket[5]) if ticket[5] else []
                items_summary = f"{len(items)} items"
                if items:
                    first_item = items[0]['name'] if 'name' in items[0] else 'Item'
                    if len(items) > 1:
                        items_summary = f"{first_item} + {len(items)-1} more"
                    else:
                        items_summary = first_item
            except:
                items_summary = "No items"
            
            items_item = QTableWidgetItem(items_summary)
            self.tickets_table.setItem(row, 4, items_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            view_btn = QPushButton("View")
            view_btn.setStyleSheet("""
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
            view_btn.clicked.connect(lambda checked, t=ticket: self.view_ticket(t))
            
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
            delete_btn.clicked.connect(lambda checked, t=ticket: self.delete_ticket(t))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(delete_btn)
            actions_widget.setLayout(actions_layout)
            
            self.tickets_table.setCellWidget(row, 5, actions_widget)
    
    def view_ticket(self, ticket):
        """View ticket details"""
        dialog = TicketViewDialog(self, ticket)
        dialog.exec_()
    
    def delete_ticket(self, ticket):
        """Delete ticket"""
        reply = QMessageBox.question(self, "Delete Ticket", 
                                   f"Are you sure you want to delete ticket #{ticket[1]}?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                cursor = self.parent.conn.cursor()
                cursor.execute('DELETE FROM tickets WHERE id = ?', (ticket[0],))
                self.parent.conn.commit()
                QMessageBox.information(self, "Success", "Ticket deleted successfully!")
                self.load_tickets()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete ticket: {str(e)}")

class TicketViewDialog(QDialog):
    def __init__(self, parent, ticket):
        super().__init__(parent)
        self.parent = parent
        self.ticket = ticket
        self.setWindowTitle(f"Ticket #{ticket[1]} Details")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header info
        header_layout = QVBoxLayout()
        
        title_label = QLabel(f"Ticket #{self.ticket[1]}")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        
        date_label = QLabel(f"Date: {self.ticket[2]}")
        date_label.setStyleSheet("font-size: 14px; color: #666;")
        
        total_label = QLabel(f"Total: {self.ticket[3]:.2f} DA")
        total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #28a745;")
        
        discount_label = QLabel(f"Discount: {self.ticket[4]:.2f} DA")
        discount_label.setStyleSheet("font-size: 14px; color: #dc3545;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(date_label)
        header_layout.addWidget(total_label)
        header_layout.addWidget(discount_label)
        
        # Items table
        items_label = QLabel("Items:")
        items_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        
        items_table = QTableWidget()
        items_table.setColumnCount(4)
        items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Price", "Total"])
        
        try:
            items = json.loads(self.ticket[5]) if self.ticket[5] else []
            items_table.setRowCount(len(items))
            
            for row, item in enumerate(items):
                items_table.setItem(row, 0, QTableWidgetItem(item.get('name', 'Unknown')))
                items_table.setItem(row, 1, QTableWidgetItem(str(item.get('quantity', 0))))
                items_table.setItem(row, 2, QTableWidgetItem(f"{item.get('price', 0):.2f} DA"))
                total = item.get('quantity', 0) * item.get('price', 0)
                items_table.setItem(row, 3, QTableWidgetItem(f"{total:.2f} DA"))
        except:
            items_table.setRowCount(1)
            items_table.setItem(0, 0, QTableWidgetItem("Error loading items"))
        
        items_table.horizontalHeader().setStretchLastSection(True)
        items_table.setAlternatingRowColors(True)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        layout.addLayout(header_layout)
        layout.addWidget(items_label)
        layout.addWidget(items_table)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
