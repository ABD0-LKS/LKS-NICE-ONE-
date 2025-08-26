<<<<<<< HEAD
# Store Manager - Professional POS System

A comprehensive Point of Sale (POS) system built with PyQt5 and SQLite, designed for retail stores and businesses.

## Features

### 🛒 Point of Sale
- **Intuitive POS Interface**: Easy-to-use touch-friendly interface
- **Product Selection**: Quick product buttons with stock indicators
- **Real-time Calculations**: Automatic total, tax, and change calculations
- **Multiple Payment Methods**: Cash, card, and other payment options
- **Receipt Printing**: Professional receipt generation and printing
- **Customer Management**: Add and manage customer information

### 📦 Inventory Management
- **Product Management**: Add, edit, and delete products
- **Stock Tracking**: Real-time inventory levels with low stock alerts
- **Category Organization**: Organize products by categories
- **Barcode Support**: Barcode scanning and management
- **Price Management**: Separate buy and sell prices

### 📊 Sales Analytics
- **Dashboard**: Comprehensive sales overview and analytics
- **Daily Reports**: Daily sales summaries and statistics
- **Ticket Management**: View and manage all sales transactions
- **Export Features**: Export data to CSV and other formats

### 👥 User Management
- **Multi-user Support**: Multiple user accounts with role-based access
- **User Roles**: Admin, Manager, and Cashier roles
- **Account Management**: User profile and password management
- **Activity Tracking**: Track user activities and sales

### ⚙️ System Features
- **Modern UI**: Clean, professional interface with dark/light themes
- **Database Management**: SQLite database with backup/restore
- **Settings Management**: Configurable store settings
- **Keyboard Shortcuts**: Efficient keyboard navigation
- **Multi-language Support**: Ready for localization

## Installation

### Prerequisites
- Python 3.7 or higher
- PyQt5

### Quick Setup

1. **Clone or download the project**
   \`\`\`bash
   git clone <repository-url>
   cd store-manager-pos
   \`\`\`

2. **Install dependencies**
   \`\`\`bash
   pip install PyQt5
   \`\`\`

3. **Initialize the database**
   \`\`\`bash
   python database_setup.py
   \`\`\`

4. **Run the application**
   \`\`\`bash
   python main.py
   \`\`\`

### Alternative Startup Methods

You can also use these convenient startup scripts:

\`\`\`bash
# Using the run script
python run_pos.py

# Using the simple start script
python start.py
\`\`\`

## Default Login

- **Username**: `admin`
- **Password**: `admin123`

## Usage Guide

### Getting Started

1. **Login**: Use the default credentials to log in
2. **Setup Store**: Go to Settings to configure your store information
3. **Add Products**: Use Product Management to add your inventory
4. **Start Selling**: Use the POS interface to process sales

### Main Menu Navigation

- **F1**: Dashboard - View sales analytics and reports
- **F2**: Settings - Configure system settings
- **F3**: Point of Sale - Process sales transactions
- **F4**: Day State - View daily sales summary
- **F5**: Account - Manage user account

### POS Interface

The POS interface includes:
- **Product Buttons**: Click to add products to cart
- **Transaction Table**: View and modify cart items
- **Payment Section**: Enter payment and calculate change
- **Control Buttons**: Various functions like calculator, keyboard, etc.

### Product Management

- **Add Products**: Click "Add Product" to create new items
- **Edit Products**: Click "Edit" in the actions column
- **Stock Levels**: Color-coded stock indicators (Green: Good, Yellow: Low, Red: Out)
- **Categories**: Organize products by categories for easy management

### Reports and Analytics

- **Dashboard**: Real-time sales overview with charts and statistics
- **Day State**: Detailed daily sales reports
- **Ticket Management**: View all sales transactions with filtering options
- **Export**: Export data to CSV for external analysis

## Database Structure

The system uses SQLite with the following main tables:
- `users` - User accounts and authentication
- `products` - Product inventory and pricing
- `customers` - Customer information
- `tickets` - Sales transactions
- `settings` - System configuration
- `daily_reports` - Daily sales summaries

## Customization

### Adding New Features

The system is designed to be extensible. You can:
- Add new widgets by creating classes that inherit from `QWidget`
- Extend the database by modifying `database_setup.py`
- Customize the UI by modifying the stylesheets in each widget

### Styling

The application uses modern CSS-like styling with:
- Consistent color scheme
- Responsive design
- Professional appearance
- Customizable themes

## Troubleshooting

### Common Issues

1. **Database Error**: Run `python database_setup.py` to recreate the database
2. **PyQt5 Not Found**: Install with `pip install PyQt5`
3. **Permission Errors**: Run as administrator or check file permissions
4. **Display Issues**: Ensure your system supports the required screen resolution

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure the database file has proper permissions
4. Try recreating the database if data issues occur

## System Requirements

- **Operating System**: Windows 7+, macOS 10.12+, or Linux
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB for application, additional space for data
- **Display**: 1024x768 minimum resolution

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Support

For support and questions, please open an issue in the project repository.

---

**Store Manager POS System** - Professional retail management made simple.
=======
# Open project in Vercel

*Automatically synced with your [v0.dev](https://v0.dev) deployments*

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/lakasmohammeda-gmailcoms-projects/v0-open-project-in-vercel)
[![Built with v0](https://img.shields.io/badge/Built%20with-v0.dev-black?style=for-the-badge)](https://v0.dev/chat/projects/9OmYhyPCzAK)

## Overview

This repository will stay in sync with your deployed chats on [v0.dev](https://v0.dev).
Any changes you make to your deployed app will be automatically pushed to this repository from [v0.dev](https://v0.dev).

## Deployment

Your project is live at:

**[https://vercel.com/lakasmohammeda-gmailcoms-projects/v0-open-project-in-vercel](https://vercel.com/lakasmohammeda-gmailcoms-projects/v0-open-project-in-vercel)**

## Build your app

Continue building your app on:

**[https://v0.dev/chat/projects/9OmYhyPCzAK](https://v0.dev/chat/projects/9OmYhyPCzAK)**

## How It Works

1. Create and modify your project using [v0.dev](https://v0.dev)
2. Deploy your chats from the v0 interface
3. Changes are automatically pushed to this repository
4. Vercel deploys the latest version from this repository
>>>>>>> eb6cfd378b248a2316c14ef227ac73f20ae5e438
