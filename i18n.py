# Simple i18n helper. Keep LTR even for Arabic; only translate labels.
from typing import Dict

_current_lang = "en"

def set_language(lang: str):
    global _current_lang
    _current_lang = "ar" if str(lang).lower().startswith("ar") else "en"

def tr(key: str, **kwargs) -> str:
    k = key.strip().upper()
    text = _STRINGS.get(k, {}).get(_current_lang, _STRINGS.get(k, {}).get("en", k))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text

_STRINGS: Dict[str, Dict[str, str]] = {
    # Login / common
    "WELCOME_BACK": {"en": "Welcome Back!", "ar": "مرحباً بعودتك!"},
    "USERNAME": {"en": "Username", "ar": "اسم المستخدم"},
    "PASSWORD": {"en": "Password", "ar": "كلمة المرور"},
    "SIGN_IN": {"en": "Sign In", "ar": "تسجيل الدخول"},
    "APP_TITLE": {"en": "STORE MANAGER", "ar": "مدير المتجر"},

    # Main Menu titles
    "DASHBOARD": {"en": "Dashboard", "ar": "لوحة التحكم"},
    "POS": {"en": "POS", "ar": "نقطة البيع"},
    "PRODUCTS": {"en": "Products", "ar": "المنتجات"},
    "TICKETS": {"en": "Tickets", "ar": "الفواتير"},
    "SETTINGS": {"en": "Settings", "ar": "الإعدادات"},
    "DAY STATE": {"en": "Day State", "ar": "حالة اليوم"},
    "ACCOUNT": {"en": "Account", "ar": "الحساب"},
    "REPORTS": {"en": "Reports", "ar": "التقارير"},

    # Main Menu descriptions
    "VIEW_ANALYTICS": {"en": "View analytics", "ar": "عرض التحليلات"},
    "PROCESS_SALES": {"en": "Process sales", "ar": "إجراء المبيعات"},
    "MANAGE_STOCK": {"en": "Manage stock", "ar": "إدارة المخزون"},
    "SALES_HISTORY": {"en": "Sales history", "ar": "سجل المبيعات"},
    "SYSTEM_CONFIG": {"en": "System config", "ar": "إعدادات النظام"},
    "DAILY_SUMMARY": {"en": "Daily summary", "ar": "ملخص يومي"},
    "USER_PROFILE": {"en": "User profile", "ar": "الملف الشخصي"},
    "GENERATE_REPORTS": {"en": "Generate reports", "ar": "إنشاء التقارير"},
    "MAIN_MENU_WELCOME": {"en": "LKS Point of Sale System", "ar": "نظام نقطة البيع LKS"},

    # POS top bar / buttons
    "SCAN": {"en": "Scan", "ar": "مسح"},
    "CONTROL_PANEL": {"en": "Control Panel", "ar": "لوحة التحكم"},
    "QUICK_ADD": {"en": "Quick Add", "ar": "إضافة سريعة"},
    "PRODUCTS_BTN": {"en": "Products", "ar": "المنتجات"},
    "TICKETS_BTN": {"en": "Tickets", "ar": "الفواتير"},
    "MAIN_MENU": {"en": "Main Menu", "ar": "القائمة الرئيسية"},

    # POS totals/payment
    "TOTAL": {"en": "TOTAL", "ar": "الإجمالي"},
    "PAYMENT": {"en": "PAYMENT", "ar": "الدفع"},
    "CHANGE": {"en": "CHANGE", "ar": "الباقي"},
    "CUSTOMER": {"en": "Customer:", "ar": "العميل:"},
    "NEW_CUSTOMER": {"en": "New Customer", "ar": "عميل جديد"},

    # POS control panel actions
    "MULTIPLE": {"en": "Multiple", "ar": "متعدد"},
    "UP": {"en": "Up", "ar": "فوق"},
    "BACK": {"en": "Back", "ar": "رجوع"},
    "LEFT": {"en": "Left", "ar": "يسار"},
    "CONFIRM": {"en": "Confirm", "ar": "تأكيد"},
    "RIGHT": {"en": "Right", "ar": "يمين"},
    "KEYBOARD": {"en": "Keyboard", "ar": "لوحة مفاتيح"},
    "DOWN": {"en": "Down", "ar": "تحت"},
    "CUSTOMER_BTN": {"en": "Customer", "ar": "العملاء"},
    "REMOVE": {"en": "Remove", "ar": "حذف"},
    "CLEAR_ALL": {"en": "Clear All", "ar": "مسح الكل"},
    "CALCULATOR": {"en": "Calculator", "ar": "آلة حاسبة"},
    "REFRESH": {"en": "Refresh", "ar": "تحديث"},
    "NEW_SALE": {"en": "New Sale", "ar": "عملية جديدة"},
    "CASH": {"en": "Cash", "ar": "نقداً"},

    # Scanner
    "BARCODE_SCANNER": {"en": "Barcode Scanner", "ar": "ماسح الباركود"},
    "START_CAMERA": {"en": "Start Camera Scan", "ar": "بدء مسح الكاميرا"},
    "STOP_CAMERA": {"en": "Stop Camera Scan", "ar": "إيقاف مسح الكاميرا"},
    "AUTO_SCAN": {"en": "Auto scan (camera)", "ar": "مسح تلقائي (كاميرا)"},
    "PROCESS_BARCODE": {"en": "Process Barcode", "ar": "معالجة الباركود"},
    "MANUAL_PRODUCT_ENTRY": {"en": "Manual Product Entry", "ar": "إدخال المنتج يدوياً"},
    "READY_TO_SCAN": {"en": "Ready to scan", "ar": "جاهز للمسح"},
    "UNKNOWN_BARCODE_TITLE": {"en": "Unknown Barcode", "ar": "باركود غير معروف"},
    "UNKNOWN_BARCODE_MSG": {"en": "Barcode {code} not found.\nIt has been logged for review.", "ar": "لم يتم العثور على الباركود {code}.\nتم حفظه للمراجعة."},
    "ADDED": {"en": "Added: {name}", "ar": "تمت إضافة: {name}"},
    "PLEASE_ENTER_BARCODE": {"en": "Please enter a barcode", "ar": "يرجى إدخال الباركود"},
    "PRODUCT_NOT_FOUND": {"en": "Product not found", "ar": "المنتج غير موجود"},

    # Sales flow
    "EMPTY_CART": {"en": "Cart is empty", "ar": "السلة فارغة"},
    "INSUFFICIENT_PAYMENT": {"en": "Payment is less than total", "ar": "المبلغ أقل من الإجمالي"},
    "SALE_COMPLETED": {"en": "Sale Completed", "ar": "تمت عملية البيع"},
}
