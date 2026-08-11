"""
Resources and styling for the CRISPR desktop application
LARGE FONTS for better readability
"""

# Modern dark theme with accent colors - LARGER FONTS
DARK_STYLE = """
QMainWindow {
    background-color: #1a1a2e;
}

QWidget {
    background-color: transparent;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}

QLabel {
    color: #e0e0e0;
    font-size: 13px;
}

QLabel#title_label {
    font-size: 28px;
    font-weight: bold;
    color: #8be9fd;
}

QLabel#subtitle_label {
    font-size: 16px;
    color: #888;
}

QLabel#stats_label {
    font-size: 14px;
    font-weight: bold;
    padding: 5px;
}

QGroupBox {
    border: 2px solid #2a2a4a;
    border-radius: 10px;
    margin-top: 15px;
    font-weight: bold;
    font-size: 15px;
    color: #8be9fd;
    background-color: rgba(26, 26, 46, 0.8);
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 10px;
    font-size: 15px;
}

QPushButton {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #4a90e2, stop: 1 #2c5f8a);
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    color: white;
    font-weight: bold;
    font-size: 14px;
    min-height: 35px;
}

QPushButton:hover {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #5ba0f2, stop: 1 #3c6f9a);
}

QPushButton:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #2c5f8a, stop: 1 #1a3f6a);
}

QPushButton:disabled {
    background-color: #3a3a5a;
    color: #888;
}

QPushButton#run_btn {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #4CAF50, stop: 1 #388E3C);
    font-size: 16px;
    padding: 14px 35px;
    min-height: 45px;
}

QPushButton#run_btn:hover {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #66BB6A, stop: 1 #43A047);
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #16213e;
    border: 2px solid #2a2a4a;
    border-radius: 8px;
    padding: 12px;
    color: #e0e0e0;
    font-size: 13px;
    font-family: 'Consolas', 'Courier New', monospace;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #4a90e2;
}

QComboBox {
    background-color: #16213e;
    border: 2px solid #2a2a4a;
    border-radius: 8px;
    padding: 10px 15px;
    color: #e0e0e0;
    min-height: 35px;
    font-size: 13px;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #8be9fd;
    margin-right: 12px;
}

QComboBox:hover {
    border: 2px solid #4a90e2;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    border: 2px solid #2a2a4a;
    selection-background-color: #4a90e2;
    font-size: 13px;
}

QTableWidget {
    background-color: #16213e;
    border: 2px solid #2a2a4a;
    border-radius: 8px;
    gridline-color: #2a2a4a;
    selection-background-color: #4a90e2;
    font-size: 13px;
}

QTableWidget::item {
    padding: 10px 12px;
}

QHeaderView::section {
    background-color: #1a1a2e;
    padding: 12px;
    border: 1px solid #2a2a4a;
    font-weight: bold;
    color: #8be9fd;
    font-size: 13px;
}

QTabWidget::pane {
    border: 2px solid #2a2a4a;
    border-radius: 10px;
    background-color: rgba(26, 26, 46, 0.5);
    padding: 10px;
}

QTabBar::tab {
    background-color: #1a1a2e;
    border: 2px solid #2a2a4a;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 14px 28px;
    margin-right: 5px;
    color: #888;
    font-weight: bold;
    font-size: 14px;
    min-width: 100px;
}

QTabBar::tab:selected {
    background-color: #2a2a4a;
    color: #8be9fd;
    border-bottom: 2px solid #4a90e2;
}

QTabBar::tab:hover:!selected {
    background-color: #222244;
    color: #ccc;
}

QScrollBar:vertical {
    background-color: #1a1a2e;
    width: 14px;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background-color: #4a90e2;
    border-radius: 7px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5ba0f2;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QProgressBar {
    background-color: #16213e;
    border: 2px solid #2a2a4a;
    border-radius: 8px;
    text-align: center;
    color: white;
    font-weight: bold;
    font-size: 13px;
    min-height: 25px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 #4a90e2, stop: 1 #8be9fd);
    border-radius: 6px;
}

QMessageBox {
    background-color: #1a1a2e;
}

QMessageBox QLabel {
    color: #e0e0e0;
    font-size: 13px;
}

QMessageBox QPushButton {
    min-width: 80px;
}

QMenuBar {
    background-color: #1a1a2e;
    color: #e0e0e0;
    border-bottom: 2px solid #2a2a4a;
    font-size: 13px;
}

QMenuBar::item:selected {
    background-color: #4a90e2;
    padding: 5px 10px;
}

QMenu {
    background-color: #1a1a2e;
    border: 2px solid #2a2a4a;
    font-size: 13px;
}

QMenu::item:selected {
    background-color: #4a90e2;
}

QStatusBar {
    background-color: #1a1a2e;
    color: #888;
    border-top: 1px solid #2a2a4a;
    font-size: 13px;
    min-height: 30px;
}

QCheckBox {
    spacing: 12px;
    color: #e0e0e0;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #2a2a4a;
    border-radius: 4px;
    background-color: #16213e;
}

QCheckBox::indicator:checked {
    background-color: #4a90e2;
    border: 2px solid #4a90e2;
}

QRadioButton {
    spacing: 12px;
    color: #e0e0e0;
    font-size: 13px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #2a2a4a;
    border-radius: 10px;
    background-color: #16213e;
}

QRadioButton::indicator:checked {
    background-color: #4a90e2;
    border: 2px solid #4a90e2;
}

QSpinBox, QDoubleSpinBox {
    background-color: #16213e;
    border: 2px solid #2a2a4a;
    border-radius: 8px;
    padding: 8px 12px;
    color: #e0e0e0;
    min-height: 35px;
    font-size: 13px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #4a90e2;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    width: 20px;
    background-color: #2a2a4a;
}

QSlider::groove:horizontal {
    border: 1px solid #2a2a4a;
    height: 10px;
    background: #16213e;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    background: #4a90e2;
    border: 1px solid #4a90e2;
    width: 22px;
    margin: -6px 0;
    border-radius: 11px;
}

QSlider::handle:horizontal:hover {
    background: #5ba0f2;
}

QListWidget, QTreeWidget {
    background-color: #16213e;
    border: 2px solid #2a2a4a;
    border-radius: 8px;
    font-size: 13px;
}

QListWidget::item, QTreeWidget::item {
    padding: 8px;
}

QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #4a90e2;
}
"""

# Light theme alternative with larger fonts
LIGHT_STYLE = """
QMainWindow {
    background-color: #f5f7fa;
}

QWidget {
    background-color: transparent;
    color: #2c3e50;
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}

QLabel {
    color: #2c3e50;
    font-size: 13px;
}

QLabel#title_label {
    font-size: 28px;
    font-weight: bold;
    color: #2980b9;
}

QLabel#subtitle_label {
    font-size: 16px;
    color: #7f8c8d;
}

QLabel#stats_label {
    font-size: 14px;
    font-weight: bold;
    padding: 5px;
}

QGroupBox {
    border: 2px solid #dce1e8;
    border-radius: 10px;
    margin-top: 15px;
    font-weight: bold;
    font-size: 15px;
    color: #2980b9;
    background-color: rgba(255, 255, 255, 0.8);
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 10px;
    font-size: 15px;
}

QPushButton {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #3498db, stop: 1 #2980b9);
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    color: white;
    font-weight: bold;
    font-size: 14px;
    min-height: 35px;
}

QPushButton:hover {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #5dade2, stop: 1 #3498db);
}

QPushButton:pressed {
    background-color: #2980b9;
}

QPushButton#run_btn {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #27ae60, stop: 1 #229954);
    font-size: 16px;
    padding: 14px 35px;
    min-height: 45px;
}

QPushButton#run_btn:hover {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #2ecc71, stop: 1 #27ae60);
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: white;
    border: 2px solid #dce1e8;
    border-radius: 8px;
    padding: 12px;
    color: #2c3e50;
    font-size: 13px;
    font-family: 'Consolas', 'Courier New', monospace;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #3498db;
}

QComboBox {
    background-color: white;
    border: 2px solid #dce1e8;
    border-radius: 8px;
    padding: 10px 15px;
    color: #2c3e50;
    min-height: 35px;
    font-size: 13px;
}

QComboBox:hover {
    border: 2px solid #3498db;
}

QComboBox QAbstractItemView {
    background-color: white;
    border: 2px solid #dce1e8;
    selection-background-color: #3498db;
    font-size: 13px;
}

QTableWidget {
    background-color: white;
    border: 2px solid #dce1e8;
    border-radius: 8px;
    gridline-color: #e8ecf1;
    selection-background-color: #3498db;
    font-size: 13px;
}

QTableWidget::item {
    padding: 10px 12px;
}

QHeaderView::section {
    background-color: #f5f7fa;
    padding: 12px;
    border: 1px solid #dce1e8;
    font-weight: bold;
    color: #2980b9;
    font-size: 13px;
}

QTabWidget::pane {
    border: 2px solid #dce1e8;
    border-radius: 10px;
    background-color: rgba(255, 255, 255, 0.5);
    padding: 10px;
}

QTabBar::tab {
    background-color: #f5f7fa;
    border: 2px solid #dce1e8;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 14px 28px;
    margin-right: 5px;
    color: #888;
    font-weight: bold;
    font-size: 14px;
    min-width: 100px;
}

QTabBar::tab:selected {
    background-color: white;
    color: #2980b9;
    border-bottom: 2px solid #3498db;
}

QProgressBar {
    background-color: white;
    border: 2px solid #dce1e8;
    border-radius: 8px;
    text-align: center;
    color: #2c3e50;
    font-weight: bold;
    font-size: 13px;
    min-height: 25px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 #3498db, stop: 1 #5dade2);
    border-radius: 6px;
}

QSpinBox, QDoubleSpinBox {
    background-color: white;
    border: 2px solid #dce1e8;
    border-radius: 8px;
    padding: 8px 12px;
    color: #2c3e50;
    min-height: 35px;
    font-size: 13px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #3498db;
}
"""

# Icon resources
ICON_PATHS = {
    'app': 'icons/app_icon.png',
    'open': 'icons/open.png',
    'save': 'icons/save.png',
    'run': 'icons/run.png',
    'export': 'icons/export.png',
    'settings': 'icons/settings.png',
    'help': 'icons/help.png',
    'about': 'icons/about.png'
}