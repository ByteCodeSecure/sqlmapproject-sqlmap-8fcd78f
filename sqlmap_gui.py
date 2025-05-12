#!/usr/bin/env python3

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QTextEdit, QTabWidget, QComboBox, QCheckBox, 
                             QGroupBox, QSpinBox, QFileDialog, QMessageBox,
                             QProgressBar, QSplitter, QScrollArea, QFormLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPalette, QColor, QFont, QIcon

# Import sqlmap core functionality
from sqlmap import main as sqlmap_main
from lib.core.data import conf, cmdLineOptions
from lib.core.option import initOptions
from lib.parse.cmdline import cmdLineParser

class SqlmapWorker(QThread):
    progress = Signal(str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, options):
        super().__init__()
        self.options = options

    def run(self):
        try:
            # Initialize sqlmap with GUI options
            cmdLineOptions.update(self.options)
            initOptions(cmdLineOptions)
            sqlmap_main()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class SqlmapGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLMap GUI")
        self.setMinimumSize(1200, 800)
        
        # Set modern dark theme with purple text and dark green buttons
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
                color: #b19cd9;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #b19cd9;
            }
            QPushButton {
                background-color: #0d3b1c;
                color: #ffffff;
                border: 1px solid #1e5631;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e5631;
                border: 1px solid #2a7a45;
            }
            QPushButton:pressed {
                background-color: #2a7a45;
            }
            QLineEdit, QTextEdit {
                background-color: #2d2d2d;
                color: #b19cd9;
                border: 1px solid #3d3d3d;
                padding: 6px;
                border-radius: 3px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #6a4c93;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #b19cd9;
                border: 1px solid #3d3d3d;
                padding: 6px;
                border-radius: 3px;
            }
            QComboBox:drop-down {
                border: 0px;
            }
            QComboBox:down-arrow {
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #b19cd9;
                selection-background-color: #3d3d3d;
            }
            QGroupBox {
                border: 1px solid #3d3d3d;
                margin-top: 12px;
                padding-top: 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #9370db;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: #b19cd9;
                gridline-color: #3d3d3d;
                border-radius: 3px;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #9370db;
                padding: 6px;
                border: 1px solid #3d3d3d;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #b19cd9;
                padding: 8px 15px;
                border: 1px solid #3d3d3d;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
                border-bottom: 2px solid #9370db;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3d3d3d;
            }
            QCheckBox {
                color: #b19cd9;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #0d3b1c;
                border: 1px solid #1e5631;
            }
            QSpinBox {
                background-color: #2d2d2d;
                color: #b19cd9;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 3px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #3d3d3d;
                width: 16px;
                border-radius: 2px;
            }
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                background-color: #2d2d2d;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #0d3b1c;
                width: 10px;
                margin: 0.5px;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2d2d2d;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3d3d3d;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4d4d4d;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QLabel {
                color: #b19cd9;
            }
        """)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Target Tab
        target_tab = QWidget()
        target_layout = QVBoxLayout(target_tab)
        
        # URL input
        url_group = QGroupBox("Target URL")
        url_layout = QVBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter target URL (e.g., http://example.com/vuln.php?id=1)")
        url_layout.addWidget(self.url_input)
        url_group.setLayout(url_layout)
        target_layout.addWidget(url_group)

        # Request Method
        method_group = QGroupBox("Request Method")
        method_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE"])
        method_layout.addWidget(self.method_combo)
        method_group.setLayout(method_layout)
        target_layout.addWidget(method_group)

        # Data to POST
        data_group = QGroupBox("POST Data")
        data_layout = QVBoxLayout()
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Enter POST data (e.g., id=1&user=admin)")
        data_layout.addWidget(self.data_input)
        data_group.setLayout(data_layout)
        target_layout.addWidget(data_group)

        # HTTP Headers
        headers_group = QGroupBox("HTTP Headers")
        headers_layout = QVBoxLayout()
        self.headers_table = QTableWidget()
        self.headers_table.setColumnCount(2)
        self.headers_table.setHorizontalHeaderLabels(["Header", "Value"])
        self.headers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        headers_layout.addWidget(self.headers_table)
        add_header_btn = QPushButton("Add Header")
        add_header_btn.clicked.connect(self.add_header_row)
        headers_layout.addWidget(add_header_btn)
        headers_group.setLayout(headers_layout)
        target_layout.addWidget(headers_group)

        # Cookies
        cookies_group = QGroupBox("Cookies")
        cookies_layout = QVBoxLayout()
        self.cookies_input = QLineEdit()
        self.cookies_input.setPlaceholderText("Enter cookies (e.g., PHPSESSID=1234; security=low)")
        cookies_layout.addWidget(self.cookies_input)
        cookies_group.setLayout(cookies_layout)
        target_layout.addWidget(cookies_group)

        # Proxy Settings
        proxy_group = QGroupBox("Proxy Settings")
        proxy_layout = QFormLayout()
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://proxy:port")
        proxy_layout.addRow("Proxy:", self.proxy_input)
        self.proxy_creds_input = QLineEdit()
        self.proxy_creds_input.setPlaceholderText("username:password")
        proxy_layout.addRow("Credentials:", self.proxy_creds_input)
        proxy_group.setLayout(proxy_layout)
        target_layout.addWidget(proxy_group)

        # Options Tab
        options_tab = QWidget()
        options_layout = QVBoxLayout(options_tab)

        # Level and Risk
        level_risk_group = QGroupBox("Level and Risk")
        level_risk_layout = QHBoxLayout()
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 5)
        self.level_spin.setValue(1)
        level_risk_layout.addWidget(QLabel("Level:"))
        level_risk_layout.addWidget(self.level_spin)
        self.risk_spin = QSpinBox()
        self.risk_spin.setRange(1, 3)
        self.risk_spin.setValue(1)
        level_risk_layout.addWidget(QLabel("Risk:"))
        level_risk_layout.addWidget(self.risk_spin)
        level_risk_group.setLayout(level_risk_layout)
        options_layout.addWidget(level_risk_group)

        # Techniques
        techniques_group = QGroupBox("Techniques")
        techniques_layout = QVBoxLayout()
        self.techniques = {
            "B": QCheckBox("Boolean-based blind"),
            "E": QCheckBox("Error-based"),
            "U": QCheckBox("Union query-based"),
            "S": QCheckBox("Stacked queries"),
            "T": QCheckBox("Time-based blind"),
            "Q": QCheckBox("Inline queries")
        }
        for checkbox in self.techniques.values():
            techniques_layout.addWidget(checkbox)
        techniques_group.setLayout(techniques_layout)
        options_layout.addWidget(techniques_group)

        # Database
        db_group = QGroupBox("Database")
        db_layout = QFormLayout()
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["Auto", "MySQL", "PostgreSQL", "Oracle", "Microsoft SQL Server", "SQLite"])
        db_layout.addRow("Database Type:", self.db_type_combo)
        self.db_name_input = QLineEdit()
        self.db_name_input.setPlaceholderText("Database name")
        db_layout.addRow("Database Name:", self.db_name_input)
        db_group.setLayout(db_layout)
        options_layout.addWidget(db_group)

        # OS Command
        os_group = QGroupBox("OS Command")
        os_layout = QFormLayout()
        self.os_cmd_check = QCheckBox("Enable OS command execution")
        os_layout.addRow(self.os_cmd_check)
        self.os_cmd_input = QLineEdit()
        self.os_cmd_input.setPlaceholderText("Command to execute")
        os_layout.addRow("Command:", self.os_cmd_input)
        os_group.setLayout(os_layout)
        options_layout.addWidget(os_group)

        # File System
        fs_group = QGroupBox("File System")
        fs_layout = QFormLayout()
        self.fs_check = QCheckBox("Enable file system access")
        fs_layout.addRow(self.fs_check)
        self.fs_path_input = QLineEdit()
        self.fs_path_input.setPlaceholderText("File path")
        fs_layout.addRow("Path:", self.fs_path_input)
        fs_group.setLayout(fs_layout)
        options_layout.addWidget(fs_group)

        # Detection Tab
        detection_tab = QWidget()
        detection_layout = QVBoxLayout(detection_tab)

        # Fingerprint
        fingerprint_group = QGroupBox("Fingerprint")
        fingerprint_layout = QVBoxLayout()
        self.fingerprint_check = QCheckBox("Enable database fingerprinting")
        fingerprint_layout.addWidget(self.fingerprint_check)
        fingerprint_group.setLayout(fingerprint_layout)
        detection_layout.addWidget(fingerprint_group)

        # Tables
        tables_group = QGroupBox("Tables")
        tables_layout = QFormLayout()
        self.tables_check = QCheckBox("Enable table enumeration")
        tables_layout.addRow(self.tables_check)
        self.tables_input = QLineEdit()
        self.tables_input.setPlaceholderText("Table names (comma-separated)")
        tables_layout.addRow("Tables:", self.tables_input)
        tables_group.setLayout(tables_layout)
        detection_layout.addWidget(tables_group)

        # Columns
        columns_group = QGroupBox("Columns")
        columns_layout = QFormLayout()
        self.columns_check = QCheckBox("Enable column enumeration")
        columns_layout.addRow(self.columns_check)
        self.columns_input = QLineEdit()
        self.columns_input.setPlaceholderText("Column names (comma-separated)")
        columns_layout.addRow("Columns:", self.columns_input)
        columns_group.setLayout(columns_layout)
        detection_layout.addWidget(columns_group)

        # Data
        data_group = QGroupBox("Data")
        data_layout = QFormLayout()
        self.data_check = QCheckBox("Enable data dumping")
        data_layout.addRow(self.data_check)
        self.data_limit_spin = QSpinBox()
        self.data_limit_spin.setRange(1, 1000)
        self.data_limit_spin.setValue(100)
        data_layout.addRow("Limit:", self.data_limit_spin)
        data_group.setLayout(data_layout)
        detection_layout.addWidget(data_group)

        # Search
        search_group = QGroupBox("Search")
        search_layout = QFormLayout()
        self.search_check = QCheckBox("Enable search")
        search_layout.addRow(self.search_check)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search pattern")
        search_layout.addRow("Pattern:", self.search_input)
        search_group.setLayout(search_layout)
        detection_layout.addWidget(search_group)

        # Optimization Tab
        optimization_tab = QWidget()
        optimization_layout = QVBoxLayout(optimization_tab)

        # Threads
        threads_group = QGroupBox("Threads")
        threads_layout = QFormLayout()
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 10)
        self.threads_spin.setValue(1)
        threads_layout.addRow("Number of threads:", self.threads_spin)
        threads_group.setLayout(threads_layout)
        optimization_layout.addWidget(threads_group)

        # Timeout
        timeout_group = QGroupBox("Timeout")
        timeout_layout = QFormLayout()
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(30)
        timeout_layout.addRow("Timeout (seconds):", self.timeout_spin)
        timeout_group.setLayout(timeout_layout)
        optimization_layout.addWidget(timeout_group)

        # Retry
        retry_group = QGroupBox("Retry")
        retry_layout = QFormLayout()
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 10)
        self.retry_spin.setValue(3)
        retry_layout.addRow("Retry attempts:", self.retry_spin)
        retry_group.setLayout(retry_layout)
        optimization_layout.addWidget(retry_group)

        # Batch
        batch_group = QGroupBox("Batch Mode")
        batch_layout = QVBoxLayout()
        self.batch_check = QCheckBox("Enable batch mode")
        batch_layout.addWidget(self.batch_check)
        batch_group.setLayout(batch_layout)
        optimization_layout.addWidget(batch_group)

        # Output Tab
        output_tab = QWidget()
        output_layout = QVBoxLayout(output_tab)
        
        # Output text area with custom styling
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #b19cd9;
                border: 1px solid #3d3d3d;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        output_layout.addWidget(self.output_text)

        # Progress bar with custom styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% Complete")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                background-color: #2d2d2d;
                text-align: center;
                color: white;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #0d3b1c;
                border-radius: 3px;
            }
        """)
        output_layout.addWidget(self.progress_bar)

        # Export options
        export_group = QGroupBox("Export")
        export_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        export_layout.addWidget(self.export_btn)
        export_group.setLayout(export_layout)
        output_layout.addWidget(export_group)

        # Add tabs
        tabs.addTab(target_tab, "Target")
        tabs.addTab(options_tab, "Options")
        tabs.addTab(detection_tab, "Detection")
        tabs.addTab(optimization_tab, "Optimization")
        tabs.addTab(output_tab, "Output")

        # Start button with enhanced styling
        start_button = QPushButton("Start SQLMap")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #0d3b1c;
                color: white;
                border: 1px solid #1e5631;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #1e5631;
                border: 1px solid #2a7a45;
            }
            QPushButton:pressed {
                background-color: #2a7a45;
            }
        """)
        start_button.clicked.connect(self.start_sqlmap)
        layout.addWidget(start_button)

        # Initialize worker
        self.worker = None

    def add_header_row(self):
        row = self.headers_table.rowCount()
        self.headers_table.insertRow(row)
        self.headers_table.setItem(row, 0, QTableWidgetItem(""))
        self.headers_table.setItem(row, 1, QTableWidgetItem(""))

    def export_results(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Results", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.output_text.toPlainText())
                QMessageBox.information(self, "Success", "Results exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export results: {str(e)}")

    def start_sqlmap(self):
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.warning(self, "Warning", "SQLMap is already running!")
            return

        # Get options from GUI
        options = {
            "url": self.url_input.text(),
            "method": self.method_combo.currentText(),
            "data": self.data_input.text(),
            "level": self.level_spin.value(),
            "risk": self.risk_spin.value(),
            "techniques": "".join([k for k, v in self.techniques.items() if v.isChecked()]),
            "headers": self.get_headers(),
            "cookies": self.cookies_input.text(),
            "proxy": self.proxy_input.text(),
            "proxy-cred": self.proxy_creds_input.text(),
            "dbms": self.db_type_combo.currentText().lower() if self.db_type_combo.currentText() != "Auto" else None,
            "db": self.db_name_input.text() or None,
            "os-cmd": self.os_cmd_input.text() if self.os_cmd_check.isChecked() else None,
            "file-read": self.fs_path_input.text() if self.fs_check.isChecked() else None,
            "fingerprint": self.fingerprint_check.isChecked(),
            "tables": self.tables_input.text() if self.tables_check.isChecked() else None,
            "columns": self.columns_input.text() if self.columns_check.isChecked() else None,
            "dump": self.data_check.isChecked(),
            "limit": self.data_limit_spin.value(),
            "search": self.search_input.text() if self.search_check.isChecked() else None,
            "threads": self.threads_spin.value(),
            "timeout": self.timeout_spin.value(),
            "retries": self.retry_spin.value(),
            "batch": self.batch_check.isChecked()
        }

        # Validate URL
        if not options["url"]:
            QMessageBox.critical(self, "Error", "Please enter a target URL!")
            return

        # Create and start worker
        self.worker = SqlmapWorker(options)
        self.worker.progress.connect(self.update_output)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def get_headers(self):
        headers = {}
        for row in range(self.headers_table.rowCount()):
            header = self.headers_table.item(row, 0)
            value = self.headers_table.item(row, 1)
            if header and value and header.text() and value.text():
                headers[header.text()] = value.text()
        return headers

    def update_output(self, text):
        self.output_text.append(text)

    def on_finished(self):
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Success", "SQLMap scan completed!")

    def on_error(self, error):
        QMessageBox.critical(self, "Error", f"An error occurred: {error}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SqlmapGUI()
    window.show()
    sys.exit(app.exec())