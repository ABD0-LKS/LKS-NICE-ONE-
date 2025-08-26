from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta
import json
import sqlite3
import csv
import os


class ReportsWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Date range selector
        date_range = self.create_date_range_selector()
        main_layout.addWidget(date_range)
        
        # Main content with tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: palette(base);
            margin-top: -1px;
        }
        QTabBar::tab {
            background: #f3f4f6;
            padding: 12px 24px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
            color: #6b7280;
        }
        QTabBar::tab:selected {
            background: palette(base);
            color: #10b981;
            border-bottom: 2px solid #10b981;
        }
    """)
        
        # Add tabs
        tab_widget.addTab(self.create_sales_summary_tab(), "📊 Sales Summary")
        tab_widget.addTab(self.create_product_performance_tab(), "📦 Product Performance")
        tab_widget.addTab(self.create_customer_analysis_tab(), "👥 Customer Analysis")
        tab_widget.addTab(self.create_financial_report_tab(), "💰 Financial Report")
        
        main_layout.addWidget(tab_widget)
        
        # Export buttons
        export_layout = self.create_export_buttons()
        main_layout.addLayout(export_layout)
        
        self.setLayout(main_layout)
    
    def create_header(self):
        """Create header with title and back button"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        back_btn = QPushButton("← Back to Main Menu")
        back_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 140px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        back_btn.clicked.connect(self.parent.show_main_menu)
        
        title = QLabel("Business Reports & Analytics")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #2c3e50;
            margin-left: 20px;
        """)
        
        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        
        header_layout.addWidget(back_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        
        return header
    
    def create_date_range_selector(self):
        """Create date range selection widget"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Date range label
        range_label = QLabel("Report Period:")
        range_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #495057;")
        
        # From date
        from_label = QLabel("From:")
        from_label.setStyleSheet("font-size: 14px; color: #6c757d; margin-left: 20px;")
        
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                min-width: 120px;
            }
        """)
        self.from_date.dateChanged.connect(self.load_data)
        
        # To date
        to_label = QLabel("To:")
        to_label.setStyleSheet("font-size: 14px; color: #6c757d; margin-left: 15px;")
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setStyleSheet(self.from_date.styleSheet())
        self.to_date.dateChanged.connect(self.load_data)
        
        # Quick select buttons
        quick_btns_layout = QHBoxLayout()
        quick_buttons = [
            ("Today", 0),
            ("Last 7 Days", 7),
            ("Last 30 Days", 30),
            ("This Month", -1)
        ]
        
        for btn_text, days in quick_buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    background: #f8f9fa;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    margin-left: 5px;
                }
                QPushButton:hover {
                    background: #e9ecef;
                }
            """)
            btn.clicked.connect(lambda checked, d=days: self.set_quick_date_range(d))
            quick_btns_layout.addWidget(btn)
        
        layout.addWidget(range_label)
        layout.addWidget(from_label)
        layout.addWidget(self.from_date)
        layout.addWidget(to_label)
        layout.addWidget(self.to_date)
        layout.addLayout(quick_btns_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def set_quick_date_range(self, days):
        """Set quick date ranges"""
        today = QDate.currentDate()
        
        if days == 0:  # Today
            self.from_date.setDate(today)
            self.to_date.setDate(today)
        elif days == -1:  # This month
            first_day = QDate(today.year(), today.month(), 1)
            self.from_date.setDate(first_day)
            self.to_date.setDate(today)
        else:  # Last N days
            self.from_date.setDate(today.addDays(-days))
            self.to_date.setDate(today)
    
    def create_sales_summary_tab(self):
        """Create sales summary tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # KPI Cards
        kpi_layout = QHBoxLayout()
        
        self.total_sales_card = self.create_kpi_card("Total Sales", "0.00 DA", "#28a745", "💰")
        self.total_transactions_card = self.create_kpi_card("Transactions", "0", "#17a2b8", "🧾")
        self.avg_transaction_card = self.create_kpi_card("Avg Transaction", "0.00 DA", "#ffc107", "📊")
        self.items_sold_card = self.create_kpi_card("Items Sold", "0", "#6f42c1", "📦")
        
        kpi_layout.addWidget(self.total_sales_card)
        kpi_layout.addWidget(self.total_transactions_card)
        kpi_layout.addWidget(self.avg_transaction_card)
        kpi_layout.addWidget(self.items_sold_card)
        
        # Daily sales trend (text-based chart)
        trend_group = QGroupBox("📈 Daily Sales Trend")
        trend_group.setStyleSheet("""
        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background: palette(base);
        }
    """)
        
        trend_layout = QVBoxLayout()
        self.sales_trend_text = QTextEdit()
        self.sales_trend_text.setMaximumHeight(200)
        self.sales_trend_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        trend_layout.addWidget(self.sales_trend_text)
        trend_group.setLayout(trend_layout)
        
        # Transaction analysis table
        trans_group = QGroupBox("🔍 Transaction Analysis")
        trans_group.setStyleSheet("""
        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background: palette(base);
        }
    """)
        
        trans_layout = QVBoxLayout()
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(4)
        self.transaction_table.setHorizontalHeaderLabels(["Date", "Transactions", "Total Sales (DA)", "Avg Sale (DA)"])
        self.setup_table_style(self.transaction_table)
        trans_layout.addWidget(self.transaction_table)
        trans_group.setLayout(trans_layout)
        
        layout.addLayout(kpi_layout)
        layout.addWidget(trend_group)
        layout.addWidget(trans_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_product_performance_tab(self):
        """Create product performance tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Product KPIs
        product_kpi_layout = QHBoxLayout()
        
        self.top_product_card = self.create_kpi_card("Top Product", "Loading...", "#e74c3c", "🏆")
        self.total_products_card = self.create_kpi_card("Products Sold", "0", "#fd7e14", "📦")
        self.avg_profit_card = self.create_kpi_card("Avg Profit", "0.00 DA", "#20c997", "💹")
        self.low_stock_card = self.create_kpi_card("Low Stock Items", "0", "#dc3545", "⚠️")
        
        product_kpi_layout.addWidget(self.top_product_card)
        product_kpi_layout.addWidget(self.total_products_card)
        product_kpi_layout.addWidget(self.avg_profit_card)
        product_kpi_layout.addWidget(self.low_stock_card)
        
        # Top selling products
        top_products_group = QGroupBox("🔥 Top Selling Products")
        top_products_group.setStyleSheet("""
        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background: palette(base);
        }
    """)
        
        top_products_layout = QVBoxLayout()
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(5)
        self.top_products_table.setHorizontalHeaderLabels([
            "Product", "Qty Sold", "Revenue (DA)", "Profit (DA)", "Stock Level"
        ])
        self.setup_table_style(self.top_products_table)
        top_products_layout.addWidget(self.top_products_table)
        top_products_group.setLayout(top_products_layout)
        
        # Product categories performance
        categories_group = QGroupBox("📊 Category Performance")
        categories_group.setStyleSheet("""
        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background: palette(base);
        }
    """)
        
        categories_layout = QVBoxLayout()
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(4)
        self.categories_table.setHorizontalHeaderLabels([
            "Category", "Products", "Total Sales (DA)", "Avg Price (DA)"
        ])
        self.setup_table_style(self.categories_table)
        categories_layout.addWidget(self.categories_table)
        categories_group.setLayout(categories_layout)
        
        layout.addLayout(product_kpi_layout)
        layout.addWidget(top_products_group)
        layout.addWidget(categories_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_customer_analysis_tab(self):
        """Create customer analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Customer KPIs
        customer_kpi_layout = QHBoxLayout()
        
        self.total_customers_card = self.create_kpi_card("Total Customers", "0", "#6f42c1", "👥")
        self.new_customers_card = self.create_kpi_card("New Customers", "0", "#28a745", "🆕")
        self.avg_customer_value_card = self.create_kpi_card("Avg Customer Value", "0.00 DA", "#fd7e14", "💎")
        self.repeat_customers_card = self.create_kpi_card("Repeat Customers", "0%", "#17a2b8", "🔄")
        
        customer_kpi_layout.addWidget(self.total_customers_card)
        customer_kpi_layout.addWidget(self.new_customers_card)
        customer_kpi_layout.addWidget(self.avg_customer_value_card)
        customer_kpi_layout.addWidget(self.repeat_customers_card)
        
        # Top customers
        top_customers_group = QGroupBox("⭐ Top Customers")
        top_customers_group.setStyleSheet("""
        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background: palette(base);
        }
    """)
        
        top_customers_layout = QVBoxLayout()
        self.top_customers_table = QTableWidget()
        self.top_customers_table.setColumnCount(4)
        self.top_customers_table.setHorizontalHeaderLabels([
            "Customer", "Total Purchases (DA)", "Transactions", "Last Purchase"
        ])
        self.setup_table_style(self.top_customers_table)
        top_customers_layout.addWidget(self.top_customers_table)
        top_customers_group.setLayout(top_customers_layout)
        
        # Customer purchase history
        history_group = QGroupBox("📋 Recent Customer Activity")
        history_group.setStyleSheet("""
        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background: palette(base);
        }
    """)
        
        history_layout = QVBoxLayout()
        self.customer_history_table = QTableWidget()
        self.customer_history_table.setColumnCount(4)
        self.customer_history_table.setHorizontalHeaderLabels([
            "Date", "Customer", "Items", "Amount (DA)"
        ])
        self.setup_table_style(self.customer_history_table)
        history_layout.addWidget(self.customer_history_table)
        history_group.setLayout(history_layout)
        
        layout.addLayout(customer_kpi_layout)
        layout.addWidget(top_customers_group)
        layout.addWidget(history_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_financial_report_tab(self):
        """Create financial report tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Financial KPIs
        financial_kpi_layout = QHBoxLayout()
        
        self.gross_revenue_card = self.create_kpi_card("Gross Revenue", "0.00 DA", "#28a745", "💰")
        self.total_cost_card = self.create_kpi_card("Total Cost", "0.00 DA", "#dc3545", "💸")
        self.gross_profit_card = self.create_kpi_card("Gross Profit", "0.00 DA", "#20c997", "📈")
        self.profit_margin_card = self.create_kpi_card("Profit Margin", "0%", "#6f42c1", "📊")
        
        financial_kpi_layout.addWidget(self.gross_revenue_card)
        financial_kpi_layout.addWidget(self.total_cost_card)
        financial_kpi_layout.addWidget(self.gross_profit_card)
        financial_kpi_layout.addWidget(self.profit_margin_card)
        
        # Financial breakdown
        breakdown_group = QGroupBox("💹 Financial Breakdown")
        breakdown_group.setStyleSheet("""
        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background: palette(base);
        }
    """)
        
        breakdown_layout = QVBoxLayout()
        self.financial_table = QTableWidget()
        self.financial_table.setColumnCount(5)
        self.financial_table.setHorizontalHeaderLabels([
            "Date", "Revenue (DA)", "Cost (DA)", "Profit (DA)", "Margin (%)"
        ])
        self.setup_table_style(self.financial_table)
        breakdown_layout.addWidget(self.financial_table)
        breakdown_group.setLayout(breakdown_layout)
        
        # Business insights
        insights_group = QGroupBox("💡 Business Insights & Recommendations")
        insights_group.setStyleSheet("""
        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background: palette(base);
        }
    """)
        
        insights_layout = QVBoxLayout()
        self.insights_text = QTextEdit()
        self.insights_text.setMaximumHeight(150)
        self.insights_text.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        insights_layout.addWidget(self.insights_text)
        insights_group.setLayout(insights_layout)
        
        layout.addLayout(financial_kpi_layout)
        layout.addWidget(breakdown_group)
        layout.addWidget(insights_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_kpi_card(self, title, value, color, icon):
        """Create a KPI card widget"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                border-left: 4px solid {color};
                padding: 15px;
            }}
        """)
        card.setFixedHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 24px;
            color: {color};
        """)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #6c757d;
            text-transform: uppercase;
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {color};
            margin: 10px 0;
        """)
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        layout.addStretch()
        
        # Store reference for updating
        card.value_label = value_label
        return card
    
    def setup_table_style(self, table):
        """Setup consistent table styling"""
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setStyleSheet("""
        QTableWidget {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            font-size: 13px;
            gridline-color: #f1f3f4;
            background: palette(base);
            color: palette(text);
        }
        QHeaderView::section {
            background: #f3f4f6;
            padding: 10px;
            border: none;
            font-weight: 600;
            color: #374151;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #f8f9fa;
        }
        QTableWidget::item:selected {
            background: #d1fae5;
            color: #065f46;
        }
    """)
        
        # Auto-resize columns
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
    
    def create_export_buttons(self):
        """Create export buttons layout"""
        layout = QHBoxLayout()
        
        # Export to CSV
        csv_btn = QPushButton("📄 Export to CSV")
        csv_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 140px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        csv_btn.clicked.connect(self.export_to_csv)
        
        # Export to PDF (placeholder)
        pdf_btn = QPushButton("📑 Export to PDF")
        pdf_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 140px;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        pdf_btn.clicked.connect(self.export_to_pdf)
        
        # Print report
        print_btn = QPushButton("🖨️ Print Report")
        print_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 140px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        print_btn.clicked.connect(self.print_report)
        
        layout.addStretch()
        layout.addWidget(csv_btn)
        layout.addWidget(pdf_btn)
        layout.addWidget(print_btn)
        
        return layout
    
    def load_data(self):
        """Load all report data"""
        try:
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            self.load_sales_summary_data(from_date, to_date)
            self.load_product_performance_data(from_date, to_date)
            self.load_customer_analysis_data(from_date, to_date)
            self.load_financial_report_data(from_date, to_date)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load report data: {str(e)}")
    
    def load_sales_summary_data(self, from_date, to_date):
        """Load sales summary data"""
        try:
            cursor = self.parent.conn.cursor()
            
            # Get overall stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as transactions,
                    COALESCE(SUM(total_price), 0) as total_sales,
                    COALESCE(AVG(total_price), 0) as avg_transaction
                FROM tickets 
                WHERE date BETWEEN ? AND ?
            """, (from_date, to_date + " 23:59:59"))
            
            stats = cursor.fetchone()
            
            # Get total items sold
            cursor.execute("""
                SELECT COALESCE(SUM(
                    json_extract(value, '$.quantity')
                ), 0)
                FROM tickets, json_each(tickets.items)
                WHERE date BETWEEN ? AND ?
            """, (from_date, to_date + " 23:59:59"))
            
            items_sold = cursor.fetchone()[0] or 0
            
            # Update KPI cards
            self.total_sales_card.value_label.setText(f"{stats[1]:,.2f} DA")
            self.total_transactions_card.value_label.setText(f"{stats[0]:,}")
            self.avg_transaction_card.value_label.setText(f"{stats[2]:,.2f} DA")
            self.items_sold_card.value_label.setText(f"{items_sold:,}")
            
            # Load daily breakdown
            cursor.execute("""
                SELECT 
                    DATE(date) as sale_date,
                    COUNT(*) as transactions,
                    COALESCE(SUM(total_price), 0) as total_sales,
                    COALESCE(AVG(total_price), 0) as avg_sale
                FROM tickets 
                WHERE date BETWEEN ? AND ?
                GROUP BY DATE(date)
                ORDER BY sale_date DESC
            """, (from_date, to_date + " 23:59:59"))
            
            daily_data = cursor.fetchall()
            
            # Update transaction table
            self.transaction_table.setRowCount(len(daily_data))
            
            # Generate sales trend text
            trend_text = "Daily Sales Trend:\n" + "="*50 + "\n"
            max_sales = max([row[2] for row in daily_data]) if daily_data else 1
            
            for row, (date, transactions, sales, avg_sale) in enumerate(daily_data):
                # Add to table
                self.transaction_table.setItem(row, 0, QTableWidgetItem(date))
                self.transaction_table.setItem(row, 1, QTableWidgetItem(f"{transactions:,}"))
                self.transaction_table.setItem(row, 2, QTableWidgetItem(f"{sales:,.2f}"))
                self.transaction_table.setItem(row, 3, QTableWidgetItem(f"{avg_sale:,.2f}"))
                
                # Add to trend chart (text-based)
                bar_length = int((sales / max_sales) * 30) if max_sales > 0 else 0
                bar = "█" * bar_length
                trend_text += f"{date}: {bar} {sales:,.0f} DA\n"
            
            self.sales_trend_text.setPlainText(trend_text)
            
        except Exception as e:
            print(f"Error loading sales summary: {e}")
    
    def load_product_performance_data(self, from_date, to_date):
        """Load product performance data"""
        try:
            cursor = self.parent.conn.cursor()
            
            # Get top selling products
            cursor.execute("""
                SELECT 
                    json_extract(value, '$.name') as product_name,
                    SUM(json_extract(value, '$.quantity')) as total_quantity,
                    SUM(json_extract(value, '$.total')) as total_revenue,
                    p.price_buy,
                    p.quantity as stock_level
                FROM tickets t, json_each(t.items) 
                LEFT JOIN products p ON json_extract(value, '$.name') = p.name
                WHERE t.date BETWEEN ? AND ?
                GROUP BY product_name
                ORDER BY total_quantity DESC
                LIMIT 20
            """, (from_date, to_date + " 23:59:59"))
            
            products_data = cursor.fetchall()
            
            # Update top products table
            self.top_products_table.setRowCount(len(products_data))
            
            total_profit = 0
            products_sold = len(products_data)
            top_product = "N/A"
            
            for row, (name, qty, revenue, buy_price, stock) in enumerate(products_data):
                if row == 0:
                    top_product = name
                
                profit = revenue - (buy_price * qty) if buy_price else 0
                total_profit += profit
                
                self.top_products_table.setItem(row, 0, QTableWidgetItem(name))
                self.top_products_table.setItem(row, 1, QTableWidgetItem(f"{int(qty):,}"))
                self.top_products_table.setItem(row, 2, QTableWidgetItem(f"{revenue:,.2f}"))
                self.top_products_table.setItem(row, 3, QTableWidgetItem(f"{profit:,.2f}"))
                self.top_products_table.setItem(row, 4, QTableWidgetItem(f"{stock or 0}"))
            
            # Get low stock count
            cursor.execute("SELECT COUNT(*) FROM products WHERE quantity < 10")
            low_stock_count = cursor.fetchone()[0]
            
            # Update product KPIs
            self.top_product_card.value_label.setText(top_product)
            self.total_products_card.value_label.setText(f"{products_sold}")
            avg_profit = total_profit / products_sold if products_sold > 0 else 0
            self.avg_profit_card.value_label.setText(f"{avg_profit:,.2f} DA")
            self.low_stock_card.value_label.setText(f"{low_stock_count}")
            
            # Load category performance
            cursor.execute("""
                SELECT 
                    COALESCE(p.category, 'Uncategorized') as category,
                    COUNT(DISTINCT p.name) as product_count,
                    COALESCE(SUM(json_extract(value, '$.total')), 0) as total_sales,
                    COALESCE(AVG(json_extract(value, '$.price')), 0) as avg_price
                FROM tickets t, json_each(t.items)
                LEFT JOIN products p ON json_extract(value, '$.name') = p.name
                WHERE t.date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY total_sales DESC
            """, (from_date, to_date + " 23:59:59"))
            
            categories_data = cursor.fetchall()
            
            # Update categories table
            self.categories_table.setRowCount(len(categories_data))
            
            for row, (category, count, sales, avg_price) in enumerate(categories_data):
                self.categories_table.setItem(row, 0, QTableWidgetItem(category))
                self.categories_table.setItem(row, 1, QTableWidgetItem(f"{count}"))
                self.categories_table.setItem(row, 2, QTableWidgetItem(f"{sales:,.2f}"))
                self.categories_table.setItem(row, 3, QTableWidgetItem(f"{avg_price:,.2f}"))
            
        except Exception as e:
            print(f"Error loading product performance: {e}")
    
    def load_customer_analysis_data(self, from_date, to_date):
        """Load customer analysis data"""
        try:
            cursor = self.parent.conn.cursor()
            
            # Get customer stats
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT customer_name) as total_customers,
                    COUNT(*) as total_transactions,
                    COALESCE(SUM(total_price), 0) as total_sales
                FROM tickets 
                WHERE date BETWEEN ? AND ? AND customer_name != 'Walk-in Customer'
            """, (from_date, to_date + " 23:59:59"))
            
            customer_stats = cursor.fetchone()
            total_customers = customer_stats[0]
            total_transactions = customer_stats[1]
            total_sales = customer_stats[2]
            
            # Calculate average customer value
            avg_customer_value = total_sales / total_customers if total_customers > 0 else 0
            
            # Get new customers (first purchase in date range)
            cursor.execute("""
                SELECT COUNT(DISTINCT customer_name)
                FROM tickets t1
                WHERE t1.date BETWEEN ? AND ?
                AND t1.customer_name != 'Walk-in Customer'
                AND NOT EXISTS (
                    SELECT 1 FROM tickets t2 
                    WHERE t2.customer_name = t1.customer_name 
                    AND t2.date < ?
                )
            """, (from_date, to_date + " 23:59:59", from_date))
            
            new_customers = cursor.fetchone()[0]
            
            # Calculate repeat customer percentage
            repeat_percentage = 0
            if total_customers > 0:
                cursor.execute("""
                    SELECT COUNT(DISTINCT customer_name)
                    FROM tickets 
                    WHERE date BETWEEN ? AND ? 
                    AND customer_name != 'Walk-in Customer'
                    AND customer_name IN (
                        SELECT customer_name 
                        FROM tickets 
                        WHERE customer_name != 'Walk-in Customer'
                        GROUP BY customer_name 
                        HAVING COUNT(*) > 1
                    )
                """, (from_date, to_date + " 23:59:59"))
                
                repeat_customers = cursor.fetchone()[0]
                repeat_percentage = (repeat_customers / total_customers) * 100
            
            # Update customer KPIs
            self.total_customers_card.value_label.setText(f"{total_customers}")
            self.new_customers_card.value_label.setText(f"{new_customers}")
            self.avg_customer_value_card.value_label.setText(f"{avg_customer_value:,.2f} DA")
            self.repeat_customers_card.value_label.setText(f"{repeat_percentage:.1f}%")
            
            # Get top customers
            cursor.execute("""
                SELECT 
                    customer_name,
                    COALESCE(SUM(total_price), 0) as total_purchases,
                    COUNT(*) as transaction_count,
                    MAX(date) as last_purchase
                FROM tickets 
                WHERE date BETWEEN ? AND ? AND customer_name != 'Walk-in Customer'
                GROUP BY customer_name
                ORDER BY total_purchases DESC
                LIMIT 15
            """, (from_date, to_date + " 23:59:59"))
            
            top_customers_data = cursor.fetchall()
            
            # Update top customers table
            self.top_customers_table.setRowCount(len(top_customers_data))
            
            for row, (name, purchases, transactions, last_purchase) in enumerate(top_customers_data):
                try:
                    last_date = datetime.fromisoformat(last_purchase).strftime("%Y-%m-%d")
                except:
                    last_date = last_purchase[:10] if last_purchase else "N/A"
                
                self.top_customers_table.setItem(row, 0, QTableWidgetItem(name))
                self.top_customers_table.setItem(row, 1, QTableWidgetItem(f"{purchases:,.2f}"))
                self.top_customers_table.setItem(row, 2, QTableWidgetItem(f"{transactions}"))
                self.top_customers_table.setItem(row, 3, QTableWidgetItem(last_date))
            
            # Get recent customer activity
            cursor.execute("""
                SELECT 
                    DATE(date) as purchase_date,
                    customer_name,
                    json_array_length(items) as item_count,
                    total_price
                FROM tickets 
                WHERE date BETWEEN ? AND ? AND customer_name != 'Walk-in Customer'
                ORDER BY date DESC
                LIMIT 20
            """, (from_date, to_date + " 23:59:59"))
            
            activity_data = cursor.fetchall()
            
            # Update customer history table
            self.customer_history_table.setRowCount(len(activity_data))
            
            for row, (date, customer, items, amount) in enumerate(activity_data):
                self.customer_history_table.setItem(row, 0, QTableWidgetItem(date))
                self.customer_history_table.setItem(row, 1, QTableWidgetItem(customer))
                self.customer_history_table.setItem(row, 2, QTableWidgetItem(f"{items}"))
                self.customer_history_table.setItem(row, 3, QTableWidgetItem(f"{amount:,.2f}"))
            
        except Exception as e:
            print(f"Error loading customer analysis: {e}")
    
    def load_financial_report_data(self, from_date, to_date):
        """Load financial report data"""
        try:
            cursor = self.parent.conn.cursor()
            
            # Get financial overview
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(total_price), 0) as gross_revenue
                FROM tickets 
                WHERE date BETWEEN ? AND ?
            """, (from_date, to_date + " 23:59:59"))
            
            gross_revenue = cursor.fetchone()[0]
            
            # Calculate total cost (simplified - using buy prices)
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(
                        json_extract(value, '$.quantity') * COALESCE(p.price_buy, 0)
                    ), 0) as total_cost
                FROM tickets t, json_each(t.items)
                LEFT JOIN products p ON json_extract(value, '$.name') = p.name
                WHERE t.date BETWEEN ? AND ?
            """, (from_date, to_date + " 23:59:59"))
            
            total_cost = cursor.fetchone()[0]
            gross_profit = gross_revenue - total_cost
            profit_margin = (gross_profit / gross_revenue * 100) if gross_revenue > 0 else 0
            
            # Update financial KPIs
            self.gross_revenue_card.value_label.setText(f"{gross_revenue:,.2f} DA")
            self.total_cost_card.value_label.setText(f"{total_cost:,.2f} DA")
            self.gross_profit_card.value_label.setText(f"{gross_profit:,.2f} DA")
            self.profit_margin_card.value_label.setText(f"{profit_margin:.1f}%")
            
            # Get daily financial breakdown
            cursor.execute("""
                SELECT 
                    DATE(t.date) as sale_date,
                    COALESCE(SUM(t.total_price), 0) as daily_revenue,
                    COALESCE(SUM(
                        json_extract(value, '$.quantity') * COALESCE(p.price_buy, 0)
                    ), 0) as daily_cost
                FROM tickets t, json_each(t.items)
                LEFT JOIN products p ON json_extract(value, '$.name') = p.name
                WHERE t.date BETWEEN ? AND ?
                GROUP BY DATE(t.date)
                ORDER BY sale_date DESC
            """, (from_date, to_date + " 23:59:59"))
            
            financial_data = cursor.fetchall()
            
            # Update financial breakdown table
            self.financial_table.setRowCount(len(financial_data))
            
            for row, (date, revenue, cost) in enumerate(financial_data):
                profit = revenue - cost
                margin = (profit / revenue * 100) if revenue > 0 else 0
                
                self.financial_table.setItem(row, 0, QTableWidgetItem(date))
                self.financial_table.setItem(row, 1, QTableWidgetItem(f"{revenue:,.2f}"))
                self.financial_table.setItem(row, 2, QTableWidgetItem(f"{cost:,.2f}"))
                self.financial_table.setItem(row, 3, QTableWidgetItem(f"{profit:,.2f}"))
                self.financial_table.setItem(row, 4, QTableWidgetItem(f"{margin:.1f}%"))
            
            # Generate business insights
            insights = self.generate_business_insights(gross_revenue, gross_profit, profit_margin)
            self.insights_text.setPlainText(insights)
            
        except Exception as e:
            print(f"Error loading financial report: {e}")
    
    def generate_business_insights(self, revenue, profit, margin):
        """Generate business insights and recommendations"""
        insights = "📊 BUSINESS INSIGHTS & RECOMMENDATIONS\n"
        insights += "=" * 50 + "\n\n"
        
        # Revenue analysis
        if revenue > 100000:
            insights += "✅ STRONG PERFORMANCE: Excellent revenue generation!\n"
        elif revenue > 50000:
            insights += "📈 GOOD PERFORMANCE: Solid revenue, room for growth.\n"
        else:
            insights += "⚠️ IMPROVEMENT NEEDED: Focus on increasing sales volume.\n"
        
        insights += "\n"
        
        # Profit margin analysis
        if margin > 30:
            insights += "💰 EXCELLENT MARGINS: Your pricing strategy is very effective.\n"
        elif margin > 20:
            insights += "👍 GOOD MARGINS: Healthy profit margins maintained.\n"
        elif margin > 10:
            insights += "📊 AVERAGE MARGINS: Consider optimizing costs or pricing.\n"
        else:
            insights += "🚨 LOW MARGINS: Urgent need to review costs and pricing.\n"
        
        insights += "\n📋 RECOMMENDATIONS:\n"
        insights += "• Monitor top-selling products and ensure adequate stock\n"
        insights += "• Focus marketing efforts on high-margin products\n"
        insights += "• Analyze customer purchase patterns for upselling opportunities\n"
        insights += "• Review supplier costs and negotiate better terms\n"
        insights += "• Consider loyalty programs to increase repeat customers\n"
        
        return insights
    
    def export_to_csv(self):
        """Export report data to CSV"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Report to CSV",
                f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow(['Business Report'])
                    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                    writer.writerow(['Period:', f"{self.from_date.date().toString('yyyy-MM-dd')} to {self.to_date.date().toString('yyyy-MM-dd')}"])
                    writer.writerow([])
                    
                    # Write sales summary
                    writer.writerow(['SALES SUMMARY'])
                    writer.writerow(['Total Sales:', self.total_sales_card.value_label.text()])
                    writer.writerow(['Transactions:', self.total_transactions_card.value_label.text()])
                    writer.writerow(['Average Transaction:', self.avg_transaction_card.value_label.text()])
                    writer.writerow(['Items Sold:', self.items_sold_card.value_label.text()])
                    writer.writerow([])
                    
                    # Write top products
                    writer.writerow(['TOP PRODUCTS'])
                    writer.writerow(['Product', 'Quantity Sold', 'Revenue', 'Profit', 'Stock Level'])
                    
                    for row in range(self.top_products_table.rowCount()):
                        row_data = []
                        for col in range(self.top_products_table.columnCount()):
                            item = self.top_products_table.item(row, col)
                            row_data.append(item.text() if item else '')
                        writer.writerow(row_data)
                
                QMessageBox.information(self, "Export Complete", f"Report exported successfully to:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export report: {str(e)}")
    
    def export_to_pdf(self):
        """Export report to PDF (placeholder)"""
        QMessageBox.information(
            self, 
            "PDF Export", 
            "PDF export functionality will be implemented in a future update.\n\n"
            "For now, you can use the CSV export or print functionality."
        )
    
    def print_report(self):
        """Print the report (placeholder)"""
        QMessageBox.information(
            self, 
            "Print Report", 
            "Print functionality will be implemented in a future update.\n\n"
            "For now, you can export to CSV and print from your spreadsheet application."
        )
