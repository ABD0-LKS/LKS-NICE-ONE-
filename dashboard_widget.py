from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta
import json
import mysql.connector
from mysql.connector import Error
from mysql_config import get_mysql_connection


class DashboardWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        self.load_data()
        
        # Auto-refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 20)
        main_layout.setSpacing(15)

        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        # Example header: Title and date range selector

        # go to main menu button
        main_menu_btn = QPushButton("🏠 Main Menu")
        main_menu_btn.setFixedHeight(28)
        main_menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 12px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        main_menu_btn.clicked.connect(self.parent.show_main_menu)
        header_layout.addWidget(main_menu_btn)

        title_label = QLabel("Dashboard")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #333;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems(["Today", "This Week", "This Month", "All Time"])
        self.date_range_combo.setFixedWidth(140)
        self.date_range_combo.currentIndexChanged.connect(self.load_data)
        header_layout.addWidget(self.date_range_combo)

        # KPI Cards - Horizontal layout
        self.kpi_container = QWidget()
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(15)
        self.kpi_container.setLayout(self.kpi_layout)
        
        self.revenue_card = self.create_kpi_card("REVENUE", "0.00 DA", "#4CAF50", "💰", 180)
        self.transactions_card = self.create_kpi_card("TRANSACTIONS", "0", "#2196F3", "🛒", 180)
        self.products_card = self.create_kpi_card("PRODUCTS", "0", "#FFC107", "📦", 180)
        self.low_stock_card = self.create_kpi_card("LOW STOCK", "0", "#F44336", "⚠️", 180)
        
        self.kpi_layout.addWidget(self.revenue_card)
        self.kpi_layout.addWidget(self.transactions_card)
        self.kpi_layout.addWidget(self.products_card)
        self.kpi_layout.addWidget(self.low_stock_card)

        # Main content area - Split view
        self.content_splitter = QSplitter(Qt.Horizontal)

        # Left Panel - Sales Trend and Top Products
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # Sales Trend Chart
        chart_group = QGroupBox("SALES TREND")
        chart_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        chart_layout = QVBoxLayout()
        self.sales_chart = self.create_sales_chart()
        chart_layout.addWidget(self.sales_chart)
        chart_group.setLayout(chart_layout)
        left_layout.addWidget(chart_group)

        # Top Products Table
        products_group = QGroupBox("TOP PRODUCTS")
        products_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        products_layout = QVBoxLayout()
        
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(3)
        self.top_products_table.setHorizontalHeaderLabels(["PRODUCT", "QTY", "AMOUNT (DA)"])
        self.top_products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.top_products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.top_products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.top_products_table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                border: none;
            }
            QHeaderView::section {
                font-size: 14px;
                padding: 8px;
                background: #f5f5f5;
            }
        """)
        products_layout.addWidget(self.top_products_table)
        products_group.setLayout(products_layout)
        left_layout.addWidget(products_group)

        left_panel.setLayout(left_layout)

        # Right Panel - Low Stock Alerts
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        # Low Stock Alerts
        stock_group = QGroupBox("LOW STOCK ALERTS")
        stock_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #D32F2F;
                border: 1px solid #FFCDD2;
                border-radius: 8px;
            }
        """)
        stock_layout = QVBoxLayout()
        
        self.low_stock_list = QListWidget()
        self.low_stock_list.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                border: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #FFEBEE;
            }
        """)
        stock_layout.addWidget(self.low_stock_list)
        stock_group.setLayout(stock_layout)
        right_layout.addWidget(stock_group)

        right_panel.setLayout(right_layout)

        # Add panels to splitter
        self.content_splitter.addWidget(left_panel)
        self.content_splitter.addWidget(right_panel)
        self.content_splitter.setSizes([500, 300])  # Left panel gets more space

        # Add everything to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.kpi_container)
        main_layout.addWidget(self.content_splitter)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """Handle window resizing for responsive layout"""
        width = self.width()
        
        # Adjust KPI cards layout based on width
        if width < 1000:
            # Switch to 2x2 grid for smaller screens
            if self.kpi_layout.count() == 4:
                # Remove all widgets
                for i in reversed(range(self.kpi_layout.count())): 
                    self.kpi_layout.itemAt(i).widget().setParent(None)
                    
                # Create grid layout
                grid_layout = QGridLayout()
                grid_layout.addWidget(self.revenue_card, 0, 0)
                grid_layout.addWidget(self.transactions_card, 0, 1)
                grid_layout.addWidget(self.products_card, 1, 0)
                grid_layout.addWidget(self.low_stock_card, 1, 1)
                
                # Clear old layout and set new one
                QWidget().setLayout(self.kpi_layout)
                self.kpi_container.setLayout(grid_layout)
        else:
            # Switch back to horizontal layout for larger screens
            if not isinstance(self.kpi_container.layout(), QHBoxLayout):
                # Remove all widgets
                old_layout = self.kpi_container.layout()
                for i in reversed(range(old_layout.count())): 
                    old_layout.itemAt(i).widget().setParent(None)
                
                # Re-add to horizontal layout
                self.kpi_layout.addWidget(self.revenue_card)
                self.kpi_layout.addWidget(self.transactions_card)
                self.kpi_layout.addWidget(self.products_card)
                self.kpi_layout.addWidget(self.low_stock_card)
                
                self.kpi_container.setLayout(self.kpi_layout)
            
            # Adjust splitter sizes
            if width < 800:
                self.content_splitter.setOrientation(Qt.Vertical)
            else:
                self.content_splitter.setOrientation(Qt.Horizontal)
            
            super().resizeEvent(event)

    def create_kpi_card(self, title, value, color, icon, width=180):
        """Create KPI card with improved icon visibility"""
        card = QWidget()
        card.setMinimumSize(width, 120)
        card.setStyleSheet(f"""
            QWidget {{
                background: white;
                border-radius: 10px;
                border-left: 5px solid {color};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Value with icon
        value_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 36px;  /* Larger icon */
            color: {color};
        """)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {color};
        """)
        
        value_layout.addWidget(icon_label)
        value_layout.addWidget(value_label)
        value_layout.addStretch()
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #616161;
            border-top: 1px solid #EEEEEE;
            padding-top: 8px;
        """)
        
        layout.addLayout(value_layout)
        layout.addWidget(title_label)
        
        card.setLayout(layout)
        card.value_label = value_label
        
        return card
    
    def create_sales_chart(self):
        """Create responsive sales chart"""
        chart_widget = QWidget()
        chart_widget.setMinimumHeight(80)   #--------------------------------------------------------------------------------------------------------------#
        chart_widget.setStyleSheet("background: #f8f9fa; border-radius: 6px;")
        #--------------------------------------------------------------------------------------------------------------#
        self.chart_container = QVBoxLayout()
        self.chart_container.setContentsMargins(10, 10, 10, 10)
        self.chart_container.setSpacing(5)
        
        chart_widget.setLayout(self.chart_container)
        return chart_widget
    
    def load_data(self):
        """Load dashboard data based on selected period"""
        cursor = self.parent.conn.cursor()
        
        # Get date filter based on selection
        period = self.date_range_combo.currentText() if hasattr(self, 'date_range_combo') else "Today"
        date_filter = self.get_date_filter(period)
        
        # Load KPI data with proper filtering
        if date_filter:
            # Revenue for selected period
            cursor.execute("SELECT COALESCE(SUM(total_price), 0) FROM tickets WHERE date >= %s", (date_filter,))
            total_revenue = cursor.fetchone()[0]
            
            # Transaction count for selected period
            cursor.execute("SELECT COUNT(*) FROM tickets WHERE date >= %s", (date_filter,))
            total_transactions = cursor.fetchone()[0]
        else:
            # All time data
            cursor.execute("SELECT COALESCE(SUM(total_price), 0) FROM tickets")
            total_revenue = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tickets")
            total_transactions = cursor.fetchone()[0]
        
        # Update KPI cards with clear labels
        self.revenue_card.value_label.setText(f"{total_revenue:.2f} DA")
        self.transactions_card.value_label.setText(str(total_transactions))
        
        # Total products in stock
        cursor.execute("SELECT COUNT(*) FROM products WHERE quantity > 0")
        products_in_stock = cursor.fetchone()[0]
        self.products_card.value_label.setText(str(products_in_stock))
        
        # Low stock items count
        cursor.execute("SELECT COUNT(*) FROM products WHERE quantity < 10 AND quantity > 0")
        low_stock_count = cursor.fetchone()[0]
        
        # Out of stock count
        cursor.execute("SELECT COUNT(*) FROM products WHERE quantity <= 0")
        out_of_stock_count = cursor.fetchone()[0]
        
        total_alerts = low_stock_count + out_of_stock_count
        self.low_stock_card.value_label.setText(str(total_alerts))

        # Update card colors based on stock status
        if total_alerts > 0:
            self.low_stock_card.setStyleSheet("""
                QWidget {
                    background: white;
                    border: 1px solid #e9ecef;
                    border-radius: 12px;
                    border-left: 4px solid #dc3545;
                    padding: 20px;
                }
            """)
        else:
            self.low_stock_card.setStyleSheet("""
                QWidget {
                    background: white;
                    border: 1px solid #e9ecef;
                    border-radius: 12px;
                    border-left: 4px solid #28a745;
                    padding: 20px;
                }
            """)
        
        # Load detailed data
        self.load_top_products(date_filter)
        self.load_low_stock_alerts()
        self.load_chart_data(period)
    
    def get_date_filter(self, period):
        """Get date filter based on selected period"""
        now = datetime.now()
        
        if period == "Today":
            return now.strftime("%Y-%m-%d")
        elif period == "This Week":
            week_start = now - timedelta(days=now.weekday())
            return week_start.strftime("%Y-%m-%d")
        elif period == "This Month":
            return now.strftime("%Y-%m-01")
        else:  # All Time
            return None
    
    def load_top_products(self, date_filter):
        """Load top selling products with full names"""
        cursor = self.parent.conn.cursor()
        
        if date_filter:
            cursor.execute("""
                SELECT 
                    JSON_UNQUOTE(JSON_EXTRACT(items, CONCAT('$[', numbers.n, '].name'))) as product_name,
                    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(items, CONCAT('$[', numbers.n, '].quantity'))) AS UNSIGNED)) as total_quantity,
                    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(items, CONCAT('$[', numbers.n, '].total'))) AS DECIMAL(10,2))) as total_revenue
                FROM tickets
                CROSS JOIN (
                    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
                    UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9
                ) numbers
                WHERE date >= %s
                AND JSON_UNQUOTE(JSON_EXTRACT(items, CONCAT('$[', numbers.n, '].name'))) IS NOT NULL
                GROUP BY product_name
                ORDER BY total_quantity DESC
                LIMIT 10
            """, (date_filter,))
        else:
            cursor.execute("""
                SELECT 
                    JSON_UNQUOTE(JSON_EXTRACT(items, CONCAT('$[', numbers.n, '].name'))) as product_name,
                    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(items, CONCAT('$[', numbers.n, '].quantity'))) AS UNSIGNED)) as total_quantity,
                    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(items, CONCAT('$[', numbers.n, '].total'))) AS DECIMAL(10,2))) as total_revenue
                FROM tickets
                CROSS JOIN (
                    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
                    UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9
                ) numbers
                WHERE JSON_UNQUOTE(JSON_EXTRACT(items, CONCAT('$[', numbers.n, '].name'))) IS NOT NULL
                GROUP BY product_name
                ORDER BY total_quantity DESC
                LIMIT 10
            """)
        
        products = cursor.fetchall()
        self.top_products_table.setRowCount(len(products))
        
        for row, (name, quantity, revenue) in enumerate(products):
            # Full product name - no truncation
            name_item = QTableWidgetItem(str(name))
            name_item.setToolTip(str(name))  # Tooltip for very long names
            self.top_products_table.setItem(row, 0, name_item)
            
            # Quantity with proper alignment
            qty_item = QTableWidgetItem(str(int(quantity)))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.top_products_table.setItem(row, 1, qty_item)
            
            # Revenue with proper formatting
            revenue_item = QTableWidgetItem(f"{revenue:.2f}")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.top_products_table.setItem(row, 2, revenue_item)
    
    def load_low_stock_alerts(self):
        """Load specific low stock items with details"""
        cursor = self.parent.conn.cursor()
        cursor.execute("""
            SELECT name, quantity, price_sell 
            FROM products 
            WHERE quantity < 10
            ORDER BY quantity ASC, name ASC
        """)
        
        items = cursor.fetchall()
        self.low_stock_list.clear()
        
        if not items:
            self.low_stock_list.addItem("✅ All items are well stocked!")
            self.low_stock_list.item(0).setForeground(QColor("#28a745"))
        else:
            for name, quantity, price in items:
                if quantity <= 0:
                    status = "OUT OF STOCK"
                    icon = "🚫"
                elif quantity < 5:
                    status = "CRITICAL"
                    icon = "⚠️"
                else:
                    status = "LOW"
                    icon = "📉"
                
                item_text = f"{icon} {name} - {quantity} units left ({status}) - {price:.2f} DA"
                self.low_stock_list.addItem(item_text)
    
    def load_chart_data(self, period):
        """Load chart data with improved visualization"""
        cursor = self.parent.conn.cursor()
        
        # Get sales data based on period
        if period == "Today":
            # Hourly data for today
            chart_data = []
            today = datetime.now().strftime("%Y-%m-%d")
            for hour in range(24):
                hour_start = f"{today} {hour:02d}:00:00"
                hour_end = f"{today} {hour:02d}:59:59"
                cursor.execute("""
                    SELECT COALESCE(SUM(total_price), 0)
                    FROM tickets 
                    WHERE date >= %s AND date <= %s
                """, (hour_start, hour_end))
                amount = cursor.fetchone()[0]
                chart_data.append((f"{hour:02d}:00", amount))
        else:
            # Daily data for last 7 days
            chart_data = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                cursor.execute("""
                    SELECT COALESCE(SUM(total_price), 0)
                    FROM tickets 
                    WHERE DATE(date) = %s
                """, (date,))
                amount = cursor.fetchone()[0]
                day_name = (datetime.now() - timedelta(days=i)).strftime("%a")
                chart_data.append((day_name, amount))
        
        self.chart_data = list(reversed(chart_data))
        self.update_chart(period)
    
    def update_chart(self, period):
        """Update the chart with improved visualization"""
        if not self.chart_data:
            return
        
        # Clear existing layout
        if self.sales_chart.layout():
            QWidget().setLayout(self.sales_chart.layout())
        
        layout = QVBoxLayout()
        
        # Chart title
        chart_info = QLabel(f"Sales Trend - {period}")
        chart_info.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 10px;
        """)
        chart_info.setAlignment(Qt.AlignCenter)
        
        # Improved visual chart
        max_amount = max(amount for _, amount in self.chart_data) if self.chart_data else 1
        total_sales = sum(amount for _, amount in self.chart_data)
        
        # Summary stats
        stats_label = QLabel(f"Total: {total_sales:.2f} DA | Peak: {max_amount:.2f} DA")
        stats_label.setStyleSheet("""
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 15px;
        """)
        stats_label.setAlignment(Qt.AlignCenter)
        
        # Visual bar chart
        chart_text = ""
        for label, amount in self.chart_data:
            bar_length = int((amount / max_amount) * 40) if max_amount > 0 else 0
            bar = "█" * bar_length + "░" * (40 - bar_length)
            chart_text += f"{label:>6}: {bar} {amount:>7.0f} DA\n"
        
        chart_display = QLabel(chart_text)
        chart_display.setStyleSheet("""
            font-family: 'Courier New', monospace;
            font-size: 11px;
            color: #495057;
            background: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        """)
        
        layout.addWidget(chart_info)
        layout.addWidget(stats_label)
        layout.addWidget(chart_display)
        layout.addStretch()
        
        self.sales_chart.setLayout(layout)
    
    def closeEvent(self, event):
        """Clean up timer when widget is closed"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()
