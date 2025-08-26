from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QScrollArea, QGridLayout,
    QLabel, QStackedWidget, QComboBox, QTextEdit, QGroupBox, QTableWidget, QHeaderView,
    QAbstractItemView, QMessageBox, QTableWidgetItem, QDialog, QFormLayout, QSpinBox,
    QProgressDialog, QCheckBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QThread, QObject, pyqtSignal, pyqtSlot, QMetaObject, QDateTime
from PyQt5.QtGui import QColor, QPixmap, QImage
from datetime import datetime
import json
import traceback
import time
import mysql.connector
from mysql.connector import Error
from mysql_config import get_mysql_connection

from i18n import tr

# Optional camera/decoder imports with graceful fallback
try:
    import cv2
except Exception:
    cv2 = None
try:
    from pyzbar.pyzbar import decode as zbar_decode
except Exception:
    zbar_decode = None


class POSWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.cart_items = []
        self.total = 0.0
        self.selected_client = "Walk-in Customer"
        self.remise = 0.0
        self.payment_received = 0.0

        # Scan debouncing
        self._last_scanned: str = ""
        self._last_scan_at: float = 0.0
        self._scan_interval = 0.6  # seconds

        self.init_ui()
        self.load_products()

        # Timer for clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    # ---------------- UI ----------------

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Main content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # Left panel - Product buttons
        left_panel = self.create_product_panel()
        content_layout.addWidget(left_panel, 2)

        # Center panel - Transaction area
        center_panel = self.create_transaction_panel()
        content_layout.addWidget(center_panel, 3)

        # Right side - stacked views: Control Panel | Scan Panel
        self.right_stacked = QStackedWidget()
        self.control_panel = self.create_control_panel()
        self.right_stacked.addWidget(self.control_panel)
        self.barcode_panel = self.create_barcode_panel()
        self.right_stacked.addWidget(self.barcode_panel)
        self.right_stacked.setCurrentIndex(0)

        content_layout.addWidget(self.right_stacked, 2)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def create_top_bar(self):
        """Top bar with Scan and Control Panel (removed Printer, Alerts, Store Info, Receipt)."""
        top_widget = QWidget()
        top_widget.setFixedHeight(80)
        top_widget.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 0;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Left side buttons
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        scan_btn = QPushButton(f"🔍 {tr('SCAN')}")
        scan_btn.setMinimumSize(100, 40)
        scan_btn.setStyleSheet("""
            QPushButton { background: #10b981; color: #0b1021; border: none; border-radius: 6px; padding: 8px 12px; font-weight: 600; font-size: 13px; }
            QPushButton:hover { background: #34d399; }
        """)
        scan_btn.clicked.connect(self.show_scan_panel)

        control_panel_btn = QPushButton(f"⚙️ {tr('CONTROL_PANEL')}")
        control_panel_btn.setMinimumSize(120, 40)
        control_panel_btn.setStyleSheet("""
            QPushButton { background: #52525b; color: white; border: none; border-radius: 6px; padding: 8px 12px; font-weight: 600; font-size: 13px; }
            QPushButton:hover { background: #3f3f46; }
        """)
        control_panel_btn.clicked.connect(self.show_control_panel)

        buttons_layout.addWidget(scan_btn)
        buttons_layout.addWidget(control_panel_btn)

        # Keep essential nav buttons
        nav_buttons = [
            (f"➕ {tr('QUICK_ADD')}", "#22c55e", self.quick_add_product),
            (f"📋 {tr('PRODUCTS_BTN')}", "#f59e0b", self._go_products),
            (f"📄 {tr('TICKETS_BTN')}", "#ef4444", self._go_tickets),
            (f"👤 {tr('MAIN_MENU')}", "#6b7280", self._go_main_menu),
        ]
        for text, color, cb in nav_buttons:
            btn = QPushButton(text)
            btn.setMinimumSize(100, 40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color}; color: white; border: none; border-radius: 6px; padding: 8px 12px; font-weight: 600; font-size: 13px;
                }}
                QPushButton:hover {{ background: {QColor(color).darker(115).name()}; }}
            """)
            btn.clicked.connect(cb)
            buttons_layout.addWidget(btn)

        buttons_container.setLayout(buttons_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(buttons_container)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Clock
        self.datetime_widget = QWidget()
        self.datetime_widget.setFixedWidth(180)
        self.datetime_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90e2, stop:1 #357ae8);
                border-radius: 8px;
                border: 1px solid #ffffff30;
            }
        """)
        datetime_layout = QVBoxLayout()
        datetime_layout.setContentsMargins(10, 8, 10, 8)
        datetime_layout.setSpacing(2)
        now = datetime.now()
        self.date_label = QLabel(now.strftime("%d/%m/%Y"))
        self.date_label.setStyleSheet("QLabel { color: #e0f0ff; font-size: 13px; font-weight: 500; }")
        self.time_label = QLabel(now.strftime("%H:%M:%S"))
        self.time_label.setStyleSheet("QLabel { color: white; font-size: 20px; font-weight: 700; }")
        datetime_layout.addWidget(self.date_label, 0, Qt.AlignHCenter)
        datetime_layout.addWidget(self.time_label, 0, Qt.AlignHCenter)
        self.datetime_widget.setLayout(datetime_layout)

        layout.addWidget(scroll_area, 1)
        layout.addWidget(self.datetime_widget, 0, Qt.AlignRight)
        top_widget.setLayout(layout)
        return top_widget

    def create_product_panel(self):
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget { background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search products...")
        self.search_input.setStyleSheet("""
            QLineEdit { padding: 12px 16px; border: 2px solid #e9ecef; border-radius: 8px; font-size: 14px; background: #f8f9fa; }
            QLineEdit:focus { border-color: #10b981; background: white; }
        """)
        self.search_input.textChanged.connect(self.filter_products)

        clear_search_btn = QPushButton("✕")
        clear_search_btn.setFixedSize(40, 40)
        clear_search_btn.setStyleSheet("""
            QPushButton { background: #ef4444; color: white; border: none; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #dc2626; }
        """)
        clear_search_btn.clicked.connect(self.clear_search)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(clear_search_btn)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #f8f9fa; width: 12px; border-radius: 6px; }
            QScrollBar::handle:vertical { background: #dee2e6; border-radius: 6px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #adb5bd; }
        """)
        self.product_container = QWidget()
        self.product_layout = QGridLayout()
        self.product_layout.setSpacing(10)
        self.product_container.setLayout(self.product_layout)
        scroll_area.setWidget(self.product_container)

        layout.addLayout(search_layout)
        layout.addWidget(scroll_area)
        widget.setLayout(layout)
        return widget

    def create_transaction_panel(self):
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget { background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        display_widget = QWidget()
        display_widget.setStyleSheet("""
            QWidget { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8f9fa, stop:1 #e9ecef); border: 2px solid #dee2e6; border-radius: 12px; padding: 20px; }
        """)
        display_layout = QHBoxLayout()

        total_container = QVBoxLayout()
        total_label = QLabel(tr("TOTAL"))
        total_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #6c757d; margin-bottom: 5px;")
        total_label.setAlignment(Qt.AlignCenter)

        self.total_display = QLabel("0.00 DA")
        self.total_display.setStyleSheet("""
            QLabel { font-size: 42px; font-weight: 700; color: #22c55e; font-family: 'Courier New', monospace; background: white;
                     padding: 15px 25px; border-radius: 8px; border: 2px solid #22c55e; }
        """)
        self.total_display.setAlignment(Qt.AlignCenter)
        total_container.addWidget(total_label)
        total_container.addWidget(self.total_display)

        payment_container = QVBoxLayout()
        payment_label = QLabel(tr("PAYMENT"))
        payment_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #6c757d;")
        payment_label.setAlignment(Qt.AlignCenter)

        self.payment_input = QLineEdit()
        self.payment_input.setPlaceholderText("0.00")
        self.payment_input.setStyleSheet("""
            QLineEdit { font-size: 24px; font-weight: 600; color: #0ea5e9; font-family: 'Courier New', monospace; background: white;
                        padding: 10px 15px; border-radius: 6px; border: 2px solid #0ea5e9; text-align: center; }
        """)
        self.payment_input.textChanged.connect(self.calculate_change)

        change_label = QLabel(tr("CHANGE"))
        change_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #6c757d; margin-top: 10px;")
        change_label.setAlignment(Qt.AlignCenter)

        self.change_display = QLabel("0.00 DA")
        self.change_display.setStyleSheet("""
            QLabel { font-size: 20px; font-weight: 600; color: #ef4444; font-family: 'Courier New', monospace; background: white;
                     padding: 8px 12px; border-radius: 6px; border: 2px solid #ef4444; }
        """)
        self.change_display.setAlignment(Qt.AlignCenter)

        payment_container.addWidget(payment_label)
        payment_container.addWidget(self.payment_input)
        payment_container.addWidget(change_label)
        payment_container.addWidget(self.change_display)

        display_layout.addLayout(total_container, 2)
        display_layout.addLayout(payment_container, 1)
        display_widget.setLayout(display_layout)

        # Client selection
        client_widget = QWidget()
        client_widget.setStyleSheet("QWidget { background: #f8f9fa; border-radius: 8px; padding: 10px; }")
        client_layout = QHBoxLayout()
        client_label = QLabel(tr("CUSTOMER"))
        client_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #495057;")
        self.client_combo = QComboBox()
        self.client_combo.setStyleSheet("""
            QComboBox { background: white; border: 2px solid #dee2e6; border-radius: 6px; padding: 8px 12px; font-size: 14px; min-width: 150px; }
            QComboBox:focus { border-color: #10b981; }
        """)
        self.load_customers()
        new_customer_btn = QPushButton(tr("NEW_CUSTOMER"))
        new_customer_btn.setStyleSheet("""
            QPushButton { background: #22c55e; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 600; }
            QPushButton:hover { background: #16a34a; }
        """)
        new_customer_btn.clicked.connect(self.add_new_customer)
        client_layout.addWidget(client_label)
        client_layout.addWidget(self.client_combo)
        client_layout.addWidget(new_customer_btn)
        client_layout.addStretch()
        client_widget.setLayout(client_layout)

        # Transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels(["Product", "Price", "Qty", "Stock", "Total", "Action"])
        header = self.transaction_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in [1, 2, 3, 4, 5]:
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.transaction_table.setAlternatingRowColors(True)
        self.transaction_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.transaction_table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #dee2e6; border-radius: 8px; gridline-color: #f1f3f4; font-size: 13px; }
            QTableWidget::item { padding: 10px 8px; border-bottom: 1px solid #f8f9fa; }
            QTableWidget::item:selected { background: #e3f2fd; color: #1976d2; }
            QTableWidget::item:alternate { background: #f8f9fa; }
        """)

        layout.addWidget(display_widget)
        layout.addWidget(client_widget)
        layout.addWidget(self.transaction_table)
        widget.setLayout(layout)
        return widget

    def create_control_panel(self):
        widget = QWidget()
        widget.setStyleSheet("QWidget { background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; }")
        layout = QGridLayout()
        layout.setSpacing(8)
        buttons = [
            (f"📦\n{tr('MULTIPLE')}", "#f59e0b", 0, 0, self.handle_multiple),
            (f"⬆️\n{tr('UP')}", "#6d28d9", 0, 1, self.move_up),
            (f"🔙\n{tr('BACK')}", "#0ea5e9", 0, 2, self.go_back),
            (f"⬅️\n{tr('LEFT')}", "#6d28d9", 1, 0, self.move_left),
            (f"✅\n{tr('CONFIRM')}", "#22c55e", 1, 1, self.handle_confirm),
            (f"➡️\n{tr('RIGHT')}", "#6d28d9", 1, 2, self.move_right),
            (f"⌨️\n{tr('KEYBOARD')}", "#f59e0b", 2, 0, self.show_keyboard),
            (f"⬇️\n{tr('DOWN')}", "#6d28d9", 2, 1, self.move_down),
            (f"👤\n{tr('CUSTOMER_BTN')}", "#f59e0b", 2, 2, self.manage_customer),
            (f"🛒\n{tr('REMOVE')}", "#fbbf24", 3, 0, self.remove_selected),
            (f"🧹\n{tr('CLEAR_ALL')}", "#ef4444", 3, 1, self.clear_all),
            (f"🧮\n{tr('CALCULATOR')}", "#0ea5e9", 3, 2, self.show_calculator),
            (f"🔄\n{tr('REFRESH')}", "#22c55e", 4, 0, self.refresh_display),
            (f"🎫\n{tr('NEW_SALE')}", "#3b82f6", 4, 1, self.process_sale),
            (f"💰\n{tr('CASH')}", "#22c55e", 4, 2, self.quick_cash_payment),
        ]
        for text, color, row, col, cb in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color}; color: white; border: none; border-radius: 8px; padding: 12px 8px;
                    font-weight: 600; font-size: 11px; text-align: center; min-height: 60px;
                }}
                QPushButton:hover {{ opacity: 0.9; }}
                QPushButton:pressed {{ opacity: 0.8; }}
            """)
            btn.clicked.connect(cb)
            layout.addWidget(btn, row, col)
        widget.setLayout(layout)
        return widget

    def create_barcode_panel(self):
        """Right-side barcode scanning panel with USB + Camera support and auto-scan."""
        widget = QWidget()
        widget.setStyleSheet("QWidget { background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; }")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel(tr("BARCODE_SCANNER"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("QLabel { font-size: 18px; font-weight: 600; color: #333; }")

        controls = QHBoxLayout()
        self.camera_scan_btn = QPushButton(tr("START_CAMERA"))
        self.camera_scan_btn.setStyleSheet("""
            QPushButton { background: #0ea5e9; color: white; border: none; border-radius: 8px; padding: 12px; font-size: 14px; font-weight: 600; }
            QPushButton:hover { background: #0284c7; }
        """)
        self.camera_scan_btn.clicked.connect(self.toggle_camera_scan)
        self.auto_scan_checkbox = QCheckBox(tr("AUTO_SCAN"))
        self.auto_scan_checkbox.setChecked(True)
        controls.addWidget(self.camera_scan_btn)
        controls.addStretch()
        controls.addWidget(self.auto_scan_checkbox)

        self.camera_view = QLabel()
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setStyleSheet("QLabel { background-color: #f8f9fa; border: 2px dashed #dee2e6; min-height: 150px; }")
        self.camera_view.setText("Camera feed will appear here")

        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan barcode here or enter manually (USB scanner)...")
        self.barcode_input.setStyleSheet("QLineEdit { font-size: 16px; padding: 12px; border: 2px solid #0ea5e9; border-radius: 8px; text-align: center; }")
        self.barcode_input.returnPressed.connect(lambda: self.process_barcode(None))

        process_btn = QPushButton(tr("PROCESS_BARCODE"))
        process_btn.setStyleSheet("QPushButton { background: #22c55e; color: white; border: none; border-radius: 8px; padding: 12px; font-size: 14px; font-weight: 600; }")
        process_btn.clicked.connect(lambda: self.process_barcode(None))

        manual_entry_btn = QPushButton(tr("MANUAL_PRODUCT_ENTRY"))
        manual_entry_btn.setStyleSheet("QPushButton { background: #6b7280; color: white; border: none; border-radius: 8px; padding: 12px; font-size: 14px; font-weight: 600; }")
        manual_entry_btn.clicked.connect(lambda: ManualProductEntryDialog(self).exec_())

        self.barcode_status = QLabel(tr("READY_TO_SCAN"))
        self.barcode_status.setAlignment(Qt.AlignCenter)
        self.barcode_status.setStyleSheet("QLabel { font-size: 14px; color: #6c757d; }")

        layout.addWidget(title)
        layout.addLayout(controls)
        layout.addWidget(self.camera_view)
        layout.addWidget(self.barcode_input)
        layout.addWidget(process_btn)
        layout.addWidget(manual_entry_btn)
        layout.addWidget(self.barcode_status)

        widget.setLayout(layout)
        return widget

    # ------------- Barcode scanning -------------

    def show_scan_panel(self):
        self.right_stacked.setCurrentIndex(1)
        self.barcode_input.setFocus()

    def show_control_panel(self):
        self.right_stacked.setCurrentIndex(0)

    def _go_products(self):
        self._stop_camera_if_running()
        self.parent.show_product_management()

    def _go_tickets(self):
        self._stop_camera_if_running()
        self.parent.show_ticket_management()

    def _go_main_menu(self):
        self._stop_camera_if_running()
        self.parent.show_main_menu()

    def update_camera_frame(self, image: QImage):
        pix = QPixmap.fromImage(image)
        self.camera_view.setPixmap(pix.scaled(self.camera_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def update_barcode_status(self, message: str, color: str):
        self.barcode_status.setText(message)
        self.barcode_status.setStyleSheet(f"color: {color};")

    def log_unknown_barcode(self, barcode: str):
        try:
            with open("unknown_barcodes.log", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} {barcode}\n")
        except Exception:
            pass
        QMessageBox.information(self, tr("UNKNOWN_BARCODE_TITLE"), tr("UNKNOWN_BARCODE_MSG", code=barcode))

    def init_barcode_scanner(self):
        """Create worker and thread for camera scanning."""
        try:
            if cv2 is None or zbar_decode is None:
                QMessageBox.warning(self, "Scanner", "Camera scanning requires OpenCV (cv2) and pyzbar.")
                return
            self.barcode_scanner = BarcodeScanner()
            self.scanner_thread = QThread(self)
            self.barcode_scanner.moveToThread(self.scanner_thread)

            # Wire signals
            self.barcode_scanner.barcode_scanned.connect(self.on_scanned)
            self.barcode_scanner.scan_status.connect(self.update_barcode_status)
            self.barcode_scanner.unknown_barcode.connect(self.log_unknown_barcode)
            self.barcode_scanner.frame_ready.connect(self.update_camera_frame)

            self.scanner_thread.start()
        except Exception as e:
            QMessageBox.critical(self, "Scanner Error", f"Failed to initialize barcode scanner: {str(e)}")

    def toggle_camera_scan(self):
        if not hasattr(self, 'barcode_scanner'):
            self.init_barcode_scanner()
        if not hasattr(self, 'barcode_scanner'):
            return

        if self.barcode_scanner.scanning:
            QMetaObject.invokeMethod(self.barcode_scanner, "stop_scanning", Qt.QueuedConnection)
            self.camera_scan_btn.setText(tr("START_CAMERA"))
        else:
            QMetaObject.invokeMethod(self.barcode_scanner, "start_scanning", Qt.QueuedConnection)
            self.camera_scan_btn.setText(tr("STOP_CAMERA"))

    def on_scanned(self, code: str):
        if not self.auto_scan_checkbox.isChecked():
            self.update_barcode_status(f"{tr('ADDED', name=code)}", "#0ea5e9")
            return
        self.process_barcode(code)

    def process_barcode(self, barcode: str | None):
        """Unified handler for USB (input) and Camera scans."""
        code = (barcode or "").strip() if barcode else self.barcode_input.text().strip()
        if not code:
            self.update_barcode_status(tr("PLEASE_ENTER_BARCODE"), "#ef4444")
            return

        # Debounce
        now = QDateTime.currentDateTime().toMSecsSinceEpoch() / 1000.0
        if code == self._last_scanned and (now - self._last_scan_at) < self._scan_interval:
            return
        self._last_scanned = code
        self._last_scan_at = now

        try:
            cursor = self.parent.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE code_bar = ?', (code,))
            product = cursor.fetchone()

            if product:
                self.add_to_cart(product, 1)
                self.update_barcode_status(tr("ADDED", name=product[1]), "#22c55e")
                QApplication.beep()
            else:
                self.update_barcode_status(tr("PRODUCT_NOT_FOUND"), "#ef4444")
                QApplication.beep()
                self.log_unknown_barcode(code)

            if not barcode:
                self.barcode_input.clear()
        except Exception as e:
            self.update_barcode_status(f"Error: {str(e)}", "#ef4444")
            print(f"Error processing barcode: {e}")

    def _stop_camera_if_running(self):
        if hasattr(self, 'barcode_scanner') and self.barcode_scanner and self.barcode_scanner.scanning:
            QMetaObject.invokeMethod(self.barcode_scanner, "stop_scanning", Qt.QueuedConnection)
        if hasattr(self, 'scanner_thread') and self.scanner_thread:
            self.scanner_thread.quit()
            self.scanner_thread.wait(1000)

    def closeEvent(self, event):
        self._stop_camera_if_running()
        super().closeEvent(event)

    def hideEvent(self, event):
        # Stop scanning if the POS widget gets hidden or replaced
        self._stop_camera_if_running()
        super().hideEvent(event)

    # ------------- Catalog, cart & totals -------------

    def load_products(self):
        try:
            cursor = self.parent.conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY name')
            products = cursor.fetchall()

            self.clear_product_buttons()
            row, col = 0, 0
            max_cols = 3
            for product in products:
                try:
                    btn = self.create_product_button(product)
                    self.product_layout.addWidget(btn, row, col)
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Error creating button for product {product}: {e}")
                    continue
        except Exception as e:
            print(f"Error loading products: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")

    def clear_product_buttons(self):
        try:
            while self.product_layout.count():
                child = self.product_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        except Exception as e:
            print(f"Error clearing product buttons: {e}")

    def create_product_button(self, product):
        try:
            btn = QPushButton()
            btn.setFixedSize(160, 120)

            product_name = product[1] if len(product) > 1 else "Unknown"
            product_sell_price = product[4] if len(product) > 4 else 0.0
            product_quantity = product[5] if len(product) > 5 else 0

            if product_quantity <= 0:
                color = "#ef4444"
            elif product_quantity < 10:
                color = "#f59e0b"
            else:
                color = "#22c55e"

            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color}; color: white; border: none; border-radius: 10px;
                    padding: 10px; font-weight: 600; font-size: 12px; text-align: center;
                }}
                QPushButton:hover {{ opacity: 0.9; }}
                QPushButton:pressed {{ opacity: 0.8; }}
            """)
            btn.setText(f"{product_name}\n{product_sell_price:.2f} DA\nStock: {product_quantity}")
            btn.clicked.connect(lambda checked, p=product: self.add_to_cart(p, 1))
            return btn
        except Exception as e:
            print(f"Error creating product button: {e}")
            btn = QPushButton("Error\nLoading\nProduct")
            btn.setFixedSize(160, 120)
            btn.setStyleSheet("QPushButton { background: #6b7280; color: white; border: none; border-radius: 10px; padding: 10px; }")
            return btn

    def add_to_cart(self, product, quantity=1):
        """Add a product with a given quantity, with stock checks."""
        try:
            if not product or len(product) < 6:
                QMessageBox.warning(self, "Error", "Invalid product data")
                return

            product_id = product[0]
            product_name = product[1]
            product_sell_price = float(product[4])
            product_stock = int(product[5])

            if quantity <= 0:
                QMessageBox.warning(self, "Invalid Quantity", "Quantity must be positive")
                return

            if product_stock <= 0:
                QMessageBox.warning(self, "Out of Stock", f"Product '{product_name}' is out of stock!")
                return

            existing = next((i for i in self.cart_items if i['id'] == product_id), None)
            if existing:
                if existing['quantity'] + quantity <= product_stock:
                    existing['quantity'] += quantity
                else:
                    QMessageBox.warning(self, "Insufficient Stock", f"Only {product_stock} units available for '{product_name}'")
                    return
            else:
                if quantity > product_stock:
                    QMessageBox.warning(self, "Insufficient Stock", f"Only {product_stock} units available for '{product_name}'")
                    return
                self.cart_items.append({
                    'id': product_id,
                    'name': product_name,
                    'price': product_sell_price,
                    'quantity': quantity,
                    'stock': product_stock
                })

            self.update_transaction_table()
            self.update_total()
        except Exception as e:
            print(f"Error adding product to cart: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            QMessageBox.critical(self, "Error", f"Failed to add product to cart: {str(e)}")

    def load_customers(self):
        try:
            self.client_combo.clear()
            self.client_combo.addItem("Walk-in Customer")
            cursor = self.parent.conn.cursor()
            cursor.execute('SELECT name FROM customers ORDER BY name')
            for (name,) in cursor.fetchall():
                if name:
                    self.client_combo.addItem(name)
        except Exception as e:
            print(f"Error loading customers: {e}")
            if self.client_combo.count() == 0:
                self.client_combo.addItem("Walk-in Customer")

    def filter_products(self):
        try:
            search_term = self.search_input.text().lower()
            cursor = self.parent.conn.cursor()
            if search_term:
                cursor.execute('''
                    SELECT * FROM products 
                    WHERE LOWER(name) LIKE %s OR code_bar LIKE %s
                    ORDER BY name
                ''', (f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute('SELECT * FROM products ORDER BY name')
            products = cursor.fetchall()
            self.clear_product_buttons()
            row, col = 0, 0
            max_cols = 3
            for product in products:
                try:
                    btn = self.create_product_button(product)
                    self.product_layout.addWidget(btn, row, col)
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Error creating filtered product button: {e}")
        except Exception as e:
            print(f"Error filtering products: {e}")
            QMessageBox.warning(self, "Error", f"Failed to filter products: {str(e)}")

    def clear_search(self):
        try:
            self.search_input.clear()
            self.load_products()
        except Exception as e:
            print(f"Error clearing search: {e}")

    def update_transaction_table(self):
        try:
            self.transaction_table.setRowCount(len(self.cart_items))
            try:
                self.transaction_table.cellChanged.disconnect()
            except Exception:
                pass

            for row, item in enumerate(self.cart_items):
                name_item = QTableWidgetItem(str(item['name']))
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.transaction_table.setItem(row, 0, name_item)

                price_item = QTableWidgetItem(f"{item['price']:.2f}")
                price_item.setFlags(price_item.flags() & ~Qt.ItemIsEditable)
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.transaction_table.setItem(row, 1, price_item)

                qty_item = QTableWidgetItem(str(item['quantity']))
                qty_item.setTextAlignment(Qt.AlignCenter)
                self.transaction_table.setItem(row, 2, qty_item)

                stock_item = QTableWidgetItem(str(item['stock']))
                stock_item.setFlags(stock_item.flags() & ~Qt.ItemIsEditable)
                stock_item.setTextAlignment(Qt.AlignCenter)
                if item['stock'] <= 0:
                    stock_item.setBackground(QColor(248, 215, 218))
                    stock_item.setForeground(QColor(220, 53, 69))
                elif item['stock'] < 10:
                    stock_item.setBackground(QColor(255, 243, 205))
                    stock_item.setForeground(QColor(255, 193, 7))
                self.transaction_table.setItem(row, 3, stock_item)

                total_item = QTableWidgetItem(f"{item['price'] * item['quantity']:.2f}")
                total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.transaction_table.setItem(row, 4, total_item)

                remove_btn = QPushButton("✕")
                remove_btn.setStyleSheet("""
                    QPushButton { background: #ef4444; color: white; border: none; border-radius: 4px; padding: 4px 8px; font-weight: bold; }
                    QPushButton:hover { background: #dc2626; }
                """)
                remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
                self.transaction_table.setCellWidget(row, 5, remove_btn)

            self.transaction_table.cellChanged.connect(self.on_quantity_changed)
        except Exception as e:
            print(f"Error updating transaction table: {e}")

    def on_quantity_changed(self, row, column):
        try:
            if column == 2 and 0 <= row < len(self.cart_items):
                try:
                    new_qty = int(self.transaction_table.item(row, column).text())
                    if new_qty <= 0:
                        self.remove_from_cart(row)
                    elif new_qty <= self.cart_items[row]['stock']:
                        self.cart_items[row]['quantity'] = new_qty
                        self.update_transaction_table()
                        self.update_total()
                    else:
                        QMessageBox.warning(self, "Insufficient Stock", f"Only {self.cart_items[row]['stock']} units available")
                        self.update_transaction_table()
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Please enter a valid number")
                    self.update_transaction_table()
        except Exception as e:
            print(f"Error handling quantity change: {e}")

    def remove_from_cart(self, row):
        try:
            if 0 <= row < len(self.cart_items):
                del self.cart_items[row]
                self.update_transaction_table()
                self.update_total()
        except Exception as e:
            print(f"Error removing item from cart: {e}")

    def update_total(self):
        try:
            self.total = sum(item['price'] * item['quantity'] for item in self.cart_items)
            total_with_discount = self.total - self.remise
            self.total_display.setText(f"{total_with_discount:.2f} DA")
            self.calculate_change()
        except Exception as e:
            print(f"Error updating total: {e}")
            self.total_display.setText("Error")

    def calculate_change(self):
        try:
            payment = float(self.payment_input.text() or 0)
            total_with_discount = self.total - self.remise
            change = payment - total_with_discount
            if change >= 0:
                self.change_display.setText(f"{change:.2f} DA")
                self.change_display.setStyleSheet("""
                    QLabel { font-size: 20px; font-weight: 600; color: #22c55e; font-family: 'Courier New', monospace; background: white; padding: 8px 12px; border-radius: 6px; border: 2px solid #22c55e; }
                """)
            else:
                self.change_display.setText(f"{abs(change):.2f} DA")
                self.change_display.setStyleSheet("""
                    QLabel { font-size: 20px; font-weight: 600; color: #ef4444; font-family: 'Courier New', monospace; background: white; padding: 8px 12px; border-radius: 6px; border: 2px solid #ef4444; }
                """)
        except ValueError:
            self.change_display.setText("0.00 DA")
        except Exception as e:
            print(f"Error calculating change: {e}")

    def update_clock(self):
        try:
            now = datetime.now()
            self.date_label.setText(now.strftime("%d/%m/%Y"))
            self.time_label.setText(now.strftime("%H:%M:%S"))
        except Exception as e:
            print(f"Error updating clock: {e}")

    # -------- Control button handlers --------

    def quick_add_product(self):
        try:
            dialog = QuickAddProductDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open quick add dialog: {str(e)}")

    def add_new_customer(self):
        try:
            dialog = AddCustomerDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_customers()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add customer: {str(e)}")

    def handle_multiple(self):
        QMessageBox.information(self, tr("MULTIPLE"), tr("MULTIPLE"))

    def move_up(self):
        try:
            current_row = self.transaction_table.currentRow()
            if current_row > 0:
                self.transaction_table.setCurrentCell(current_row - 1, 0)
        except Exception as e:
            print(f"Error moving up: {e}")

    def move_down(self):
        try:
            current_row = self.transaction_table.currentRow()
            if current_row < self.transaction_table.rowCount() - 1:
                self.transaction_table.setCurrentCell(current_row + 1, 0)
        except Exception as e:
            print(f"Error moving down: {e}")

    def move_left(self):
        try:
            current_col = self.transaction_table.currentColumn()
            if current_col > 0:
                self.transaction_table.setCurrentCell(self.transaction_table.currentRow(), current_col - 1)
        except Exception as e:
            print(f"Error moving left: {e}")

    def move_right(self):
        try:
            current_col = self.transaction_table.currentColumn()
            if current_col < self.transaction_table.columnCount() - 1:
                self.transaction_table.setCurrentCell(self.transaction_table.currentRow(), current_col + 1)
        except Exception as e:
            print(f"Error moving right: {e}")

    def go_back(self):
        try:
            if self.cart_items:
                reply = QMessageBox.question(self, tr("BACK"), tr("BACK"),
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.parent.show_main_menu()
            else:
                self.parent.show_main_menu()
        except Exception as e:
            print(f"Error going back: {e}")

    def handle_confirm(self):
        try:
            if self.cart_items:
                self.process_sale()
            else:
                QMessageBox.warning(self, tr("EMPTY_CART"), tr("EMPTY_CART"))
        except Exception as e:
            print(f"Error handling confirm: {e}")

    def show_keyboard(self):
        try:
            keyboard_dialog = VirtualKeyboardDialog(self)
            if keyboard_dialog.exec_() == QDialog.Accepted:
                text = keyboard_dialog.get_text()
                if text:
                    self.payment_input.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show keyboard: {str(e)}")

    def manage_customer(self):
        try:
            dialog = CustomerManagementDialog(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open customer management: {str(e)}")

    def remove_selected(self):
        try:
            current_row = self.transaction_table.currentRow()
            if current_row >= 0:
                self.remove_from_cart(current_row)
            else:
                QMessageBox.information(self, "No Selection", "Please select an item to remove")
        except Exception as e:
            print(f"Error removing selected: {e}")

    def clear_all(self):
        try:
            if self.cart_items:
                reply = QMessageBox.question(self, tr("CLEAR_ALL"), tr("CLEAR_ALL"),
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.cart_items = []
                    self.remise = 0.0
                    self.payment_input.clear()
                    self.update_transaction_table()
                    self.update_total()
        except Exception as e:
            print(f"Error clearing all: {e}")

    def show_calculator(self):
        try:
            calculator_dialog = CalculatorDialog(self)
            if calculator_dialog.exec_() == QDialog.Accepted:
                result = calculator_dialog.get_result()
                self.payment_input.setText(str(result))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show calculator: {str(e)}")

    def refresh_display(self):
        try:
            self.load_products()
            self.load_customers()
            self.update_transaction_table()
            self.update_total()
            QMessageBox.information(self, tr("REFRESH"), tr("REFRESH"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh display: {str(e)}")

    def process_sale(self):
        try:
            if not self.cart_items:
                QMessageBox.warning(self, tr("EMPTY_CART"), tr("EMPTY_CART"))
                return

            try:
                payment = float(self.payment_input.text() or 0)
                total_with_discount = self.total - self.remise

                if payment < total_with_discount:
                    QMessageBox.warning(self, tr("INSUFFICIENT_PAYMENT"), tr("INSUFFICIENT_PAYMENT"))
                    return

                cursor = self.parent.conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM tickets')
                ticket_count = cursor.fetchone()[0]
                ticket_number = f"TKT{ticket_count + 1:06d}"

                items_data = []
                for item in self.cart_items:
                    items_data.append({
                        'name': item['name'],
                        'quantity': item['quantity'],
                        'price': item['price'],
                        'total': item['price'] * item['quantity']
                    })

                cursor.execute('''
                    INSERT INTO tickets (ticket_number, date, total_price, remis, payment_method, customer_name, items, status, cashier_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticket_number,
                    datetime.now().isoformat(),
                    total_with_discount,
                    self.remise,
                    'Cash',
                    self.client_combo.currentText(),
                    json.dumps(items_data),
                    'Completed',
                    self.parent.current_user['id'] if self.parent.current_user else 1
                ))

                for item in self.cart_items:
                    cursor.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?',
                                   (item['quantity'], item['id']))

                self.parent.conn.commit()

                change = payment - total_with_discount
                success_msg = f"{tr('SALE_COMPLETED')}\n\nTicket: {ticket_number}\nTotal: {total_with_discount:.2f} DA\nPayment: {payment:.2f} DA\nChange: {change:.2f} DA"
                QMessageBox.information(self, tr("SALE_COMPLETED"), success_msg)

                reply = QMessageBox.question(self, "Print Receipt", "Would you like to print the receipt?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    receipt_dialog = ReceiptDialog(self, self.cart_items, total_with_discount)
                    receipt_dialog.exec_()

                self.cart_items = []
                self.remise = 0.0
                self.payment_input.clear()
                self.update_transaction_table()
                self.update_total()
                self.load_products()
            except ValueError:
                QMessageBox.warning(self, "Invalid Payment", "Please enter a valid payment amount")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred while processing the sale: {str(e)}")
        except Exception as e:
            print(f"Critical error in process_sale: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            QMessageBox.critical(self, "Critical Error", f"A critical error occurred: {str(e)}")

    def quick_cash_payment(self):
        """Set payment to exact total (after discount)."""
        try:
            total_with_discount = self.total - self.remise
            self.payment_input.setText(f"{total_with_discount:.2f}")
        except Exception as e:
            print(f"Error setting quick cash payment: {e}")

    def process_barcode(self, code, barcode=None):
        """Process scanned barcode"""
        if not code:
            return

        now = time.time()
        if code == self._last_scanned and (now - self._last_scan_at) < self._scan_interval:
            return
        self._last_scanned = code
        self._last_scan_at = now

        try:
            cursor = self.parent.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE code_bar = %s', (code,))
            product = cursor.fetchone()

            if product:
                self.add_to_cart(product, 1)
                self.update_barcode_status(tr("ADDED", name=product[1]), "#22c55e")
                QApplication.beep()
            else:
                self.update_barcode_status(tr("PRODUCT_NOT_FOUND"), "#ef4444")
                QApplication.beep()
                self.log_unknown_barcode(code)

            if not barcode:
                self.barcode_input.clear()

        except Exception as e:
            print(f"Error processing barcode: {e}")
            self.update_barcode_status(tr("ERROR_PROCESSING"), "#ef4444")

    def log_unknown_barcode(self, code):
        """Log unknown barcode to database"""
        try:
            cursor = self.parent.conn.cursor()
            cursor.execute('''
                INSERT INTO unknown_barcodes (barcode, scan_date)
                VALUES (%s, %s)
            ''', (code, datetime.now()))
            self.parent.conn.commit()
        except Exception as e:
            print(f"Error logging unknown barcode: {e}")

    def complete_sale(self):
        """Complete the sale transaction"""
        if not self.cart_items:
            QMessageBox.warning(self, tr("EMPTY_CART"), tr("EMPTY_CART"))
            return

        try:
            total = self.calculate_total()
            total_with_discount = total - self.remise

            if total_with_discount <= 0:
                QMessageBox.warning(self, tr("INVALID_TOTAL"), tr("INVALID_TOTAL"))
                return

            # Get payment amount
            payment_dialog = PaymentDialog(self, total_with_discount)
            if payment_dialog.exec_() == QDialog.Accepted:
                payment = payment_dialog.get_payment_amount()
                
                if payment < total_with_discount:
                    QMessageBox.warning(self, tr("INSUFFICIENT_PAYMENT"), tr("INSUFFICIENT_PAYMENT"))
                    return

                cursor = self.parent.conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM tickets')
                ticket_count = cursor.fetchone()[0]
                ticket_number = f"TKT{ticket_count + 1:06d}"

                items_data = []
                for item in self.cart_items:
                    items_data.append({
                        'name': item['name'],
                        'quantity': item['quantity'],
                        'price': item['price'],
                        'total': item['price'] * item['quantity']
                    })

                cursor.execute('''
                    INSERT INTO tickets (ticket_number, date, total_price, remis, payment_method, customer_name, items, status, cashier_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    ticket_number,
                    datetime.now(),
                    total_with_discount,
                    self.remise,
                    'Cash',
                    self.client_combo.currentText(),
                    json.dumps(items_data),
                    'Completed',
                    self.parent.current_user['id'] if self.parent.current_user else 1
                ))

                for item in self.cart_items:
                    cursor.execute('UPDATE products SET quantity = quantity - %s WHERE id = %s',
                                   (item['quantity'], item['id']))

                self.parent.conn.commit()

                change = payment - total_with_discount
                success_msg = f"{tr('SALE_COMPLETED')}\n\nTicket: {ticket_number}\nTotal: {total_with_discount:.2f} DA\nPayment: {payment:.2f} DA\nChange: {change:.2f} DA"
                QMessageBox.information(self, tr("SUCCESS"), success_msg)

                # Clear cart and reset
                self.clear_cart()
                self.load_products()  # Refresh product quantities

        except Exception as e:
            print(f"Error completing sale: {e}")
            QMessageBox.critical(self, tr("ERROR"), f"{tr('SALE_ERROR')}: {str(e)}")

    def clear_cart(self):
        """Clear the cart items and reset related UI elements"""
        self.cart_items = []
        self.remise = 0.0
        self.payment_input.clear()
        self.update_transaction_table()
        self.update_total()

    def calculate_total(self):
        """Calculate the total amount of items in the cart"""
        return sum(item['price'] * item['quantity'] for item in self.cart_items)

# ---------------- BarcodeScanner worker (camera) ----------------

class BarcodeScanner(QObject):
    barcode_scanned = pyqtSignal(str)
    scan_status = pyqtSignal(str, str)   # message, color
    unknown_barcode = pyqtSignal(str)
    frame_ready = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.scanning = False
        self._cap = None
        self._timer = None
        self._last_code = ""
        self._last_time = 0.0
        self._interval = 0.5  # seconds
        self._frame_counter = 0

    @pyqtSlot()
    def start_scanning(self):
        if self.scanning:
            return
        if cv2 is None or zbar_decode is None:
            self.scan_status.emit("Camera scanning requires cv2 + pyzbar", "#ef4444")
            return
        try:
            self._cap = cv2.VideoCapture(0)
            if not self._cap or not self._cap.isOpened():
                self.scan_status.emit("Cannot open camera", "#ef4444")
                return
            self.scanning = True
            self.scan_status.emit("Camera scanning started", "#22c55e")
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._scan_step)
            self._timer.start(100)
        except Exception as e:
            self.scan_status.emit(f"Camera error: {str(e)}", "#ef4444")
            self.scanning = False

    @pyqtSlot()
    def stop_scanning(self):
        if self._timer:
            self._timer.stop()
            self._timer = None
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
        if self.scanning:
            self.scan_status.emit("Camera scanning stopped", "#6b7280")
        self.scanning = False

    def _scan_step(self):
        if not self.scanning or self._cap is None:
            return
        ok, frame = self._cap.read()
        if not ok or frame is None:
            self.scan_status.emit("Camera read failed", "#ef4444")
            return
        # Downscale to 640px width to reduce CPU
        try:
            h, w = frame.shape[:2]
            if w > 640:
                scale = 640.0 / w
                frame = cv2.resize(frame, (640, int(h * scale)))
        except Exception:
            pass

        gray = None
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except Exception:
            pass

        codes = []
        try:
            if gray is not None:
                codes = zbar_decode(gray)
            else:
                codes = zbar_decode(frame)
        except Exception:
            codes = []

        now = time.time()
        for obj in codes:
            try:
                data = obj.data.decode("utf-8").strip()
            except Exception:
                continue
            if not data:
                continue
            if data == self._last_code and (now - self._last_time) < self._interval:
                continue
            self._last_code = data
            self._last_time = now
            self.barcode_scanned.emit(data)
            self.scan_status.emit(f"Detected: {data}", "#0ea5e9")

        # Emit preview every 3rd frame only
        self._frame_counter = (self._frame_counter + 1) % 3
        if self._frame_counter == 0:
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h2, w2, ch = rgb.shape
                bytes_per_line = ch * w2
                image = QImage(rgb.data, w2, h2, bytes_per_line, QImage.Format_RGB888)
                self.frame_ready.emit(image.copy())
            except Exception:
                pass


# ---------------- Dialogs ----------------

class QuickAddProductDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Quick Add Product")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.code_input = QLineEdit()
        self.buy_price_input = QLineEdit()
        self.sell_price_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.name_input.setPlaceholderText("Product name")
        self.code_input.setPlaceholderText("Barcode (optional)")
        self.buy_price_input.setPlaceholderText("0.00")
        self.sell_price_input.setPlaceholderText("0.00")
        self.quantity_input.setPlaceholderText("0")
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Barcode:", self.code_input)
        form_layout.addRow("Buy Price:", self.buy_price_input)
        form_layout.addRow("Sell Price:", self.sell_price_input)
        form_layout.addRow("Quantity:", self.quantity_input)
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("QPushButton { background: #22c55e; color: white; padding: 10px 20px; border-radius: 6px; }")
        save_btn.clicked.connect(self.save_product)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(form_layout)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def save_product(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Product name is required")
            return
        try:
            buy_price = float(self.buy_price_input.text() or 0)
            sell_price = float(self.sell_price_input.text() or 0)
            quantity = int(self.quantity_input.text() or 0)
            cursor = self.parent.parent.conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, code_bar, price_buy, price_sell, quantity, category, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, self.code_input.text().strip(), buy_price, sell_price, quantity, 'General', datetime.now().isoformat()))
            self.parent.parent.conn.commit()
            QMessageBox.information(self, "Success", "Product added successfully!")
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")

class AddProductDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Add Product")
        self.setModal(True)
        self.resize(400, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Form fields
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.code_input = QLineEdit()
        self.buy_price_input = QLineEdit()
        self.sell_price_input = QLineEdit()
        self.quantity_input = QLineEdit()

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Barcode:", self.code_input)
        form_layout.addRow("Buy Price:", self.buy_price_input)
        form_layout.addRow("Sell Price:", self.sell_price_input)
        form_layout.addRow("Quantity:", self.quantity_input)

        # Buttons
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_product)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(form_layout)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def save_product(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Product name is required")
            return
        try:
            buy_price = float(self.buy_price_input.text() or 0)
            sell_price = float(self.sell_price_input.text() or 0)
            quantity = int(self.quantity_input.text() or 0)
            cursor = self.parent.parent.conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, code_bar, price_buy, price_sell, quantity, category, created_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (name, self.code_input.text().strip(), buy_price, sell_price, quantity, 'General', datetime.now()))
            self.parent.parent.conn.commit()
            QMessageBox.information(self, "Success", "Product added successfully!")
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")


class AddCustomerDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Add Customer")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Form fields
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Address:", self.address_input)

        # Buttons
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_customer)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(form_layout)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def save_customer(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Customer name is required")
            return
        try:
            cursor = self.parent.parent.conn.cursor()
            cursor.execute(
                '''
                INSERT INTO customers (name, phone, email, address, created_date)
                VALUES (%s, %s, %s, %s, %s)
                ''',
                (
                    name,
                    self.phone_input.text().strip(),
                    self.email_input.text().strip(),
                    self.address_input.toPlainText().strip(),
                    datetime.now()
                )
            )
            self.parent.parent.conn.commit()
            QMessageBox.information(self, "Success", "Customer added successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save customer: {str(e)}")
