from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
import json

class CalculatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculatrice")
        self.setFixedSize(300, 400)
        self.result = 0
        self.current_input = "0"
        self.previous_value = None
        self.operation = None
        self.waiting_for_operand = False
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Display
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setText("0")
        self.display.setAlignment(Qt.AlignRight)
        self.display.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                font-family: 'Courier New';
                padding: 10px;
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.display)
        
        # Buttons
        buttons_layout = QGridLayout()
        
        # Button definitions
        buttons = [
            ('C', 0, 0, 2, 1, self.clear),
            ('÷', 0, 2, 1, 1, lambda: self.operation_clicked('÷')),
            ('×', 0, 3, 1, 1, lambda: self.operation_clicked('×')),
            ('7', 1, 0, 1, 1, lambda: self.number_clicked('7')),
            ('8', 1, 1, 1, 1, lambda: self.number_clicked('8')),
            ('9', 1, 2, 1, 1, lambda: self.number_clicked('9')),
            ('-', 1, 3, 1, 1, lambda: self.operation_clicked('-')),
            ('4', 2, 0, 1, 1, lambda: self.number_clicked('4')),
            ('5', 2, 1, 1, 1, lambda: self.number_clicked('5')),
            ('6', 2, 2, 1, 1, lambda: self.number_clicked('6')),
            ('+', 2, 3, 1, 1, lambda: self.operation_clicked('+')),
            ('1', 3, 0, 1, 1, lambda: self.number_clicked('1')),
            ('2', 3, 1, 1, 1, lambda: self.number_clicked('2')),
            ('3', 3, 2, 1, 1, lambda: self.number_clicked('3')),
            ('=', 3, 3, 1, 2, self.equals_clicked),
            ('0', 4, 0, 2, 1, lambda: self.number_clicked('0')),
            ('.', 4, 2, 1, 1, lambda: self.number_clicked('.')),
        ]
        
        for text, row, col, row_span, col_span, callback in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    font-weight: bold;
                    padding: 15px;
                    border: none;
                    border-radius: 8px;
                    background-color: #4285f4;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #3367d6;
                }
                QPushButton:pressed {
                    background-color: #2c5aa0;
                }
            """)
            btn.clicked.connect(callback)
            buttons_layout.addWidget(btn, row, col, row_span, col_span)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        use_btn = QPushButton("Utiliser")
        use_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        use_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        action_layout.addWidget(use_btn)
        action_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        layout.addLayout(action_layout)
        self.setLayout(layout)
    
    def number_clicked(self, number):
        if self.waiting_for_operand:
            self.current_input = number
            self.waiting_for_operand = False
        else:
            if self.current_input == "0":
                self.current_input = number
            else:
                self.current_input += number
        
        self.display.setText(self.current_input)
    
    def operation_clicked(self, op):
        current_value = float(self.current_input)
        
        if self.previous_value is not None and not self.waiting_for_operand:
            result = self.calculate()
            self.display.setText(str(result))
            self.current_input = str(result)
            self.previous_value = result
        else:
            self.previous_value = current_value
        
        self.operation = op
        self.waiting_for_operand = True
    
    def equals_clicked(self):
        if self.previous_value is not None and self.operation:
            result = self.calculate()
            self.display.setText(str(result))
            self.current_input = str(result)
            self.previous_value = None
            self.operation = None
            self.waiting_for_operand = True
    
    def calculate(self):
        current_value = float(self.current_input)
        
        if self.operation == '+':
            return self.previous_value + current_value
        elif self.operation == '-':
            return self.previous_value - current_value
        elif self.operation == '×':
            return self.previous_value * current_value
        elif self.operation == '÷':
            if current_value != 0:
                return self.previous_value / current_value
            else:
                QMessageBox.warning(self, "Erreur", "Division par zéro!")
                return self.previous_value
        
        return current_value
    
    def clear(self):
        self.current_input = "0"
        self.previous_value = None
        self.operation = None
        self.waiting_for_operand = False
        self.display.setText("0")
    
    def get_result(self):
        return float(self.current_input)

class ClientManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Gestion des Clients")
        self.setFixedSize(600, 500)
        self.clients = []
        self.init_ui()
        self.load_clients()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Gestion des Clients")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Add client button
        add_btn = QPushButton("+ Ajouter Nouveau Client")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_btn.clicked.connect(self.add_client)
        layout.addWidget(add_btn)
        
        # Clients table
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(5)
        self.clients_table.setHorizontalHeaderLabels([
            "Nom", "Téléphone", "Email", "Adresse", "Actions"
        ])
        self.clients_table.horizontalHeader().setStretchLastSection(True)
        self.clients_table.setAlternatingRowColors(True)
        layout.addWidget(self.clients_table)
        
        # Close button
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_clients(self):
        """Load clients from database"""
        cursor = self.parent.parent.conn.cursor()
        cursor.execute('SELECT * FROM customers')
        clients = cursor.fetchall()
        
        self.clients_table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            self.clients_table.setItem(row, 0, QTableWidgetItem(client[1]))  # name
            self.clients_table.setItem(row, 1, QTableWidgetItem(client[2] or ""))  # phone
            self.clients_table.setItem(row, 2, QTableWidgetItem(client[3] or ""))  # email
            self.clients_table.setItem(row, 3, QTableWidgetItem(client[4] or ""))  # address
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            select_btn = QPushButton("Sélectionner")
            select_btn.setStyleSheet("background-color: #2196f3; color: white; padding: 5px 10px; border-radius: 4px;")
            select_btn.clicked.connect(lambda checked, c=client: self.select_client(c))
            
            edit_btn = QPushButton("Modifier")
            edit_btn.setStyleSheet("background-color: #ff9800; color: white; padding: 5px 10px; border-radius: 4px;")
            edit_btn.clicked.connect(lambda checked, c=client: self.edit_client(c))
            
            actions_layout.addWidget(select_btn)
            actions_layout.addWidget(edit_btn)
            actions_widget.setLayout(actions_layout)
            
            self.clients_table.setCellWidget(row, 4, actions_widget)
    
    def add_client(self):
        """Add new client"""
        dialog = ClientFormDialog(self, "Ajouter Client")
        if dialog.exec_() == QDialog.Accepted:
            self.load_clients()
    
    def edit_client(self, client):
        """Edit existing client"""
        dialog = ClientFormDialog(self, "Modifier Client", client)
        if dialog.exec_() == QDialog.Accepted:
            self.load_clients()
    
    def select_client(self, client):
        """Select client for current transaction"""
        self.parent.selected_client = client[1]
        self.parent.client_btn.setText(client[1])
        QMessageBox.information(self, "Client Sélectionné", f"Client '{client[1]}' sélectionné.")
        self.accept()

class ClientFormDialog(QDialog):
    def __init__(self, parent=None, title="Client", client=None):
        super().__init__(parent)
        self.parent = parent
        self.client = client
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        self.init_ui()
        
        if client:
            self.load_client_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form fields
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom du client")
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Numéro de téléphone")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Adresse email")
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Adresse complète")
        
        form_layout.addRow("Nom *:", self.name_input)
        form_layout.addRow("Téléphone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Adresse:", self.address_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setStyleSheet("background-color: #4caf50; color: white; padding: 10px 20px; border-radius: 8px;")
        save_btn.clicked.connect(self.save_client)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("background-color: #666; color: white; padding: 10px 20px; border-radius: 8px;")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def load_client_data(self):
        """Load existing client data"""
        if self.client:
            self.name_input.setText(self.client[1])
            self.phone_input.setText(self.client[2] or "")
            self.email_input.setText(self.client[3] or "")
            self.address_input.setText(self.client[4] or "")
    
    def save_client(self):
        """Save client data"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom du client est requis!")
            return
        
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()
        
        cursor = self.parent.parent.parent.conn.cursor()
        
        try:
            if self.client:  # Edit existing
                cursor.execute('''
                    UPDATE customers 
                    SET name=?, phone=?, email=?, address=?
                    WHERE id=?
                ''', (name, phone, email, address, self.client[0]))
            else:  # Add new
                cursor.execute('''
                    INSERT INTO customers (name, phone, email, address)
                    VALUES (?, ?, ?, ?)
                ''', (name, phone, email, address))
            
            self.parent.parent.parent.conn.commit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement: {str(e)}")

class PrintTicketDialog(QDialog):
    def __init__(self, parent=None, cart_items=None, total=0):
        super().__init__(parent)
        self.cart_items = cart_items or []
        self.total = total
        self.setWindowTitle("Aperçu d'Impression")
        self.setFixedSize(400, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Ticket preview
        preview_widget = QWidget()
        preview_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        preview_layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("STORE MANAGER")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        
        date_label = QLabel(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("font-size: 12px; margin-bottom: 20px;")
        
        # Items
        items_label = QLabel("Articles:")
        items_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        
        preview_layout.addWidget(header_label)
        preview_layout.addWidget(date_label)
        preview_layout.addWidget(items_label)
        
        # Items list
        for item in self.cart_items:
            item_layout = QHBoxLayout()
            item_name = QLabel(item['name'])
            item_qty = QLabel(f"x{item['quantity']}")
            item_price = QLabel(f"{item['price'] * item['quantity']:.2f} DA")
            
            item_layout.addWidget(item_name)
            item_layout.addStretch()
            item_layout.addWidget(item_qty)
            item_layout.addWidget(item_price)
            
            item_widget = QWidget()
            item_widget.setLayout(item_layout)
            preview_layout.addWidget(item_widget)
        
        # Total
        total_layout = QHBoxLayout()
        total_label = QLabel("TOTAL:")
        total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        total_value = QLabel(f"{self.total:.2f} DA")
        total_value.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(total_value)
        
        total_widget = QWidget()
        total_widget.setLayout(total_layout)
        total_widget.setStyleSheet("border-top: 2px solid #ccc; padding-top: 10px; margin-top: 10px;")
        preview_layout.addWidget(total_widget)
        
        preview_layout.addStretch()
        preview_widget.setLayout(preview_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        print_btn = QPushButton("Imprimer")
        print_btn.setStyleSheet("background-color: #4caf50; color: white; padding: 10px 20px; border-radius: 8px;")
        print_btn.clicked.connect(self.print_ticket)
        
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet("background-color: #666; color: white; padding: 10px 20px; border-radius: 8px;")
        close_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(print_btn)
        buttons_layout.addWidget(close_btn)
        
        layout.addWidget(preview_widget)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def print_ticket(self):
        """Print the ticket"""
        # In a real implementation, this would send to a printer
        QMessageBox.information(self, "Impression", "Ticket envoyé à l'imprimante!")
        self.accept()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres / Settings")
        self.setFixedSize(500, 400)
        self.current_language = "Français"
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Paramètres du Système")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Language settings
        lang_group = QGroupBox("Langue / Language")
        lang_group.setStyleSheet("QGroupBox { font-weight: bold; padding: 10px; }")
        lang_layout = QVBoxLayout()
        
        self.lang_french = QRadioButton("Français")
        self.lang_english = QRadioButton("English")
        self.lang_arabic = QRadioButton("العربية")
        
        self.lang_french.setChecked(True)  # Default
        
        lang_layout.addWidget(self.lang_french)
        lang_layout.addWidget(self.lang_english)
        lang_layout.addWidget(self.lang_arabic)
        lang_group.setLayout(lang_layout)
        
        # Store settings
        store_group = QGroupBox("Paramètres du Magasin")
        store_group.setStyleSheet("QGroupBox { font-weight: bold; padding: 10px; }")
        store_layout = QFormLayout()
        
        self.store_name = QLineEdit("STORE MANAGER")
        self.store_address = QLineEdit("123 Rue Principale")
        self.store_phone = QLineEdit("0123456789")
        self.tax_rate = QLineEdit("19.0")
        
        store_layout.addRow("Nom du magasin:", self.store_name)
        store_layout.addRow("Adresse:", self.store_address)
        store_layout.addRow("Téléphone:", self.store_phone)
        store_layout.addRow("Taux de TVA (%):", self.tax_rate)
        store_group.setLayout(store_layout)
        
        # Printer settings
        printer_group = QGroupBox("Paramètres d'Impression")
        printer_group.setStyleSheet("QGroupBox { font-weight: bold; padding: 10px; }")
        printer_layout = QFormLayout()
        
        self.printer_name = QLineEdit("Imprimante par défaut")
        self.receipt_width = QLineEdit("80")
        
        printer_layout.addRow("Imprimante:", self.printer_name)
        printer_layout.addRow("Largeur ticket (mm):", self.receipt_width)
        printer_group.setLayout(printer_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addWidget(lang_group)
        layout.addWidget(store_group)
        layout.addWidget(printer_group)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """Save settings"""
        # Get selected language
        if self.lang_french.isChecked():
            language = "Français"
        elif self.lang_english.isChecked():
            language = "English"
        else:
            language = "العربية"
        
        # Show confirmation
        QMessageBox.information(self, "Paramètres", 
                              f"Paramètres sauvegardés!\nLangue: {language}")
        self.accept()

class DayStateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("État du Jour")
        self.setFixedSize(600, 500)
        self.init_ui()
        self.load_day_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("État du Jour - " + datetime.now().strftime("%d/%m/%Y"))
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        
        # Total sales
        sales_card = self.create_summary_card("Ventes Totales", "0.00 DA", "#4caf50")
        summary_layout.addWidget(sales_card)
        
        # Total transactions
        trans_card = self.create_summary_card("Transactions", "0", "#2196f3")
        summary_layout.addWidget(trans_card)
        
        # Cash in hand
        cash_card = self.create_summary_card("Caisse", "0.00 DA", "#ff9800")
        summary_layout.addWidget(cash_card)
        
        # Today's transactions table
        table_label = QLabel("Transactions d'Aujourd'hui:")
        table_label.setStyleSheet("font-weight: bold; margin: 20px 0 10px 0;")
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(4)
        self.transactions_table.setHorizontalHeaderLabels([
            "Heure", "Client", "Total", "Statut"
        ])
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("Exporter")
        export_btn.setStyleSheet("background-color: #4caf50; color: white; padding: 10px 20px; border-radius: 8px;")
        
        print_btn = QPushButton("Imprimer")
        print_btn.setStyleSheet("background-color: #2196f3; color: white; padding: 10px 20px; border-radius: 8px;")
        
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet("background-color: #666; color: white; padding: 10px 20px; border-radius: 8px;")
        close_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(export_btn)
        buttons_layout.addWidget(print_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(summary_layout)
        layout.addWidget(table_label)
        layout.addWidget(self.transactions_table)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def create_summary_card(self, title, value, color):
        """Create summary card"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 5px;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        
        return card
    
    def load_day_data(self):
        """Load today's data"""
        # This would load actual data from database
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Sample data for demonstration
        sample_transactions = [
            ("10:30", "Client #1", "120.00 DA", "Terminé"),
            ("14:15", "Nouveau Client", "300.00 DA", "Terminé"),
        ]
        
        self.transactions_table.setRowCount(len(sample_transactions))
        
        for row, (time, client, total, status) in enumerate(sample_transactions):
            self.transactions_table.setItem(row, 0, QTableWidgetItem(time))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(client))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(total))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(status))

class SellerAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compte Vendeur")
        self.setFixedSize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Informations du Vendeur")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # User info
        info_group = QGroupBox("Informations Personnelles")
        info_layout = QFormLayout()
        
        self.username_label = QLabel("admin")
        self.role_label = QLabel("Administrateur")
        self.login_time_label = QLabel(datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        info_layout.addRow("Nom d'utilisateur:", self.username_label)
        info_layout.addRow("Rôle:", self.role_label)
        info_layout.addRow("Dernière connexion:", self.login_time_label)
        info_group.setLayout(info_layout)
        
        # Performance stats
        stats_group = QGroupBox("Statistiques de Performance")
        stats_layout = QFormLayout()
        
        self.sales_today = QLabel("2 ventes")
        self.total_today = QLabel("420.00 DA")
        self.avg_sale = QLabel("210.00 DA")
        
        stats_layout.addRow("Ventes aujourd'hui:", self.sales_today)
        stats_layout.addRow("Total aujourd'hui:", self.total_today)
        stats_layout.addRow("Vente moyenne:", self.avg_sale)
        stats_group.setLayout(stats_layout)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        
        change_password_btn = QPushButton("Changer le Mot de Passe")
        change_password_btn.setStyleSheet("background-color: #ff9800; color: white; padding: 10px; border-radius: 8px;")
        
        logout_btn = QPushButton("Se Déconnecter")
        logout_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px; border-radius: 8px;")
        logout_btn.clicked.connect(self.logout)
        
        actions_layout.addWidget(change_password_btn)
        actions_layout.addWidget(logout_btn)
        actions_group.setLayout(actions_layout)
        
        # Close button
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet("background-color: #666; color: white; padding: 10px 20px; border-radius: 8px;")
        close_btn.clicked.connect(self.accept)
        
        layout.addWidget(info_group)
        layout.addWidget(stats_group)
        layout.addWidget(actions_group)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def logout(self):
        """Logout user"""
        reply = QMessageBox.question(self, 'Déconnexion', 
                                   'Êtes-vous sûr de vouloir vous déconnecter?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.accept()
            # This would return to login screen
            QMessageBox.information(self, "Déconnexion", "Vous avez été déconnecté.")
