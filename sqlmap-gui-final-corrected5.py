    def stop_scan(self):
        if self.sqlmap_thread and self.sqlmap_thread.is_running:
            self.sqlmap_thread.stop()
            self.scan_timer.stop()
            self.output_text.append("\n[*] Escaneo detenido por el usuario")
            self.stop_button.setEnabled(False)
            
    def reset_scan(self):
        # Detener cualquier escaneo en curso
        if self.sqlmap_thread and self.sqlmap_thread.is_running:
            self.sqlmap_thread.stop()
            
        # Detener temporizador
        self.scan_timer.stop()
        
        # Restablecer la interfaz
        self.scan_form.setVisible(True)
        self.realtime_view.setVisible(False)
        self.scan_report.setVisible(False)
        
        # Limpiar salida
        self.output_text.clear()
        
        # Deshabilitar botón de detener
        self.stop_button.setEnabled(False)
        
    def update_output(self, line):
        self.output_text.append(line)
        
        # Desplazar al final
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output_text.setTextCursor(cursor)
        
        # Actualizar la salida en la pestaña de resultados
        if hasattr(self.parent, 'results_tab'):
            self.parent.results_tab.update_output(line)
        
    def update_progress(self, current, total):
        percent = int((current / total) * 100)
        self.progress_bar.setValue(percent)
        self.progress_text.setText(f"{percent}% Completado")
        
    def update_scan_time(self):
        if self.scan_start_time:
            elapsed = int(time.time() - self.scan_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.details_time.setText(f"{minutes:02d}:{seconds:02d}")
            
    def scan_completed(self, success, message):
        # Detener temporizador
        self.scan_timer.stop()
        
        # Actualizar interfaz
        self.stop_button.setEnabled(False)
        self.scan_alert.setText(message)
        
        if success:
            # Mostrar reporte de vulnerabilidad
            self.scan_report.setVisible(True)
            self.report_header.setText("Vulnerabilidad detectada")
            self.report_header.setStyleSheet(f"padding: 10px; border-radius: 4px; background-color: {COLORS['success_light']}; color: {COLORS['success_color']}; font-weight: bold;")
            
            # Extraer puntos de inyección
            output = self.output_text.toPlainText()
            injection_points = self.extract_injection_points(output)
            self.injection_points.setText(injection_points)
            
            # Actualizar estado
            self.details_status.setText("Vulnerable")
            self.details_status.setStyleSheet(f"color: {COLORS['success_color']}; font-weight: bold;")
            self.scan_alert.setStyleSheet(f"padding: 10px; border-radius: 4px; background-color: {COLORS['success_light']}; color: {COLORS['success_color']};")
            
            # Mostrar mensaje
            QMessageBox.information(self, "Escaneo completado", message)
        else:
            # Actualizar estado
            if "No se detectaron vulnerabilidades" in message:
                self.details_status.setText("No vulnerable")
                self.details_status.setStyleSheet(f"color: {COLORS['warning_color']}; font-weight: bold;")
                self.scan_alert.setStyleSheet(f"padding: 10px; border-radius: 4px; background-color: {COLORS['warning_light']}; color: {COLORS['warning_color']};")
            else:
                self.details_status.setText("Error")
                self.details_status.setStyleSheet(f"color: {COLORS['danger_color']}; font-weight: bold;")
                self.scan_alert.setStyleSheet(f"padding: 10px; border-radius: 4px; background-color: {COLORS['danger_light']}; color: {COLORS['danger_color']};")
            
            QMessageBox.warning(self, "Escaneo completado", message)
            
    def extract_injection_points(self, output):
        points = []
        pattern = r"Parameter: ([^\s]+).*?Type: ([^\s]+).*?Title: ([^\n]+)"
        matches = re.findall(pattern, output, re.DOTALL)
        
        if matches:
            result = "Puntos de inyección detectados:\n\n"
            for match in matches:
                result += f"Parámetro: {match[0]}\n"
                result += f"Tipo: {match[1]}\n"
                result += f"Título: {match[2]}\n\n"
            return result
        else:
            return "No se pudieron extraer los detalles de los puntos de inyección."
            
    def get_databases(self):
        # Cambiar a la pestaña de extracción
        if hasattr(self.parent, 'tabs'):
            # Buscar el índice de la pestaña de extracción
            for i in range(self.parent.tabs.count()):
                if self.parent.tabs.tabText(i) == "Extracción":
                    self.parent.tabs.setCurrentIndex(i)
                    break
            
            # Iniciar la extracción de bases de datos
            if hasattr(self.parent, 'extraction_tab'):
                self.parent.extraction_tab.get_databases()

# Clase principal de la aplicación
class SqlmapAutoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.setWindowTitle("SQLMap Automator")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
        
    def setup_ui(self):
        # Aplicar estilo oscuro
        self.apply_dark_style()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Pestaña de escaneo
        self.scan_tab = ScanTab(self)
        self.tabs.addTab(self.scan_tab, "Escaneo")
        
        # Pestaña de extracción
        self.extraction_tab = ExtractionTab(self)
        self.tabs.addTab(self.extraction_tab, "Extracción")
        
        # Pestaña de resultados
        self.results_tab = ResultsTab(self)
        self.tabs.addTab(self.results_tab, "Resultados")
        
        # Pestaña de ayuda
        self.help_tab = HelpTab(self)
        self.tabs.addTab(self.help_tab, "Ayuda")
        
        main_layout.addWidget(self.tabs)
        
        # Barra de estado
        self.statusBar().showMessage("Listo para escanear")
        
    def apply_dark_style(self):
        # Aplicar estilo oscuro a toda la aplicación
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(COLORS['bg_primary']))
        dark_palette.setColor(QPalette.WindowText, QColor(COLORS['text_primary']))
        dark_palette.setColor(QPalette.Base, QColor(COLORS['bg_secondary']))
        dark_palette.setColor(QPalette.AlternateBase, QColor(COLORS['bg_tertiary']))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(COLORS['text_primary']))
        dark_palette.setColor(QPalette.ToolTipText, QColor(COLORS['text_primary']))
        dark_palette.setColor(QPalette.Text, QColor(COLORS['text_primary']))
        dark_palette.setColor(QPalette.Button, QColor(COLORS['bg_tertiary']))
        dark_palette.setColor(QPalette.ButtonText, QColor(COLORS['text_primary']))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(COLORS['accent_secondary']))
        dark_palette.setColor(QPalette.Highlight, QColor(COLORS['accent_secondary']))
        dark_palette.setColor(QPalette.HighlightedText, QColor(COLORS['text_primary']))
        
        app.setPalette(dark_palette)
        
        # Estilos adicionales
        app.setStyleSheet(f"""
        QMainWindow {{
            background-color: {COLORS['bg_primary']};
        }}
        
        QWidget {{
            background-color: {COLORS['bg_primary']};
            color: {COLORS['text_primary']};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        QGroupBox {{
            border: 1px solid {COLORS['border_color']};
            border-radius: 4px;
            margin-top: 1ex;
            padding-top: 1ex;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 3px;
            color: {COLORS['text_secondary']};
        }}
        
        QPushButton {{
            background-color: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border_color']};
            padding: 5px 10px;
            border-radius: 3px;
        }}
        
        QPushButton:hover {{
            background-color: {COLORS['border_color']};
        }}
        
        QPushButton:pressed {{
            background-color: {COLORS['bg_secondary']};
        }}
        
        QLineEdit, QTextEdit, QComboBox, QSpinBox {{
            background-color: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border_color']};
            border-radius: 3px;
            padding: 3px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 1px solid {COLORS['accent_secondary']};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {COLORS['border_color']};
        }}
        
        QTabBar::tab {{
            background-color: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border_color']};
            padding: 5px 10px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {COLORS['bg_tertiary']};
            border-bottom-color: {COLORS['bg_tertiary']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {COLORS['border_color']};
        }}
        
        QProgressBar {{
            border: 1px solid {COLORS['border_color']};
            border-radius: 3px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {COLORS['accent_secondary']};
        }}
        
        QListWidget {{
            background-color: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border_color']};
            border-radius: 3px;
        }}
        
        QListWidget::item:selected {{
            background-color: {COLORS['accent_light']};
            color: {COLORS['text_primary']};
        }}
        
        QListWidget::item:hover {{
            background-color: {COLORS['border_color']};
        }}
        """)

def check_dependencies():
    """Verificar que PySide6 está instalado"""
    try:
        import PySide6
        return True
    except ImportError:
        print("PySide6 no está instalado. Instalando...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PySide6'])
            print("PySide6 instalado correctamente.")
            return True
        except subprocess.CalledProcessError:
            print("Error al instalar PySide6. Por favor, instálalo manualmente con: pip install PySide6")
            return False

def main():
    """Función principal"""
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('sqlmap.py'):
        print("Error: Este script debe ejecutarse desde el directorio raíz de SQLMap.")
        sys.exit(1)
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Iniciar la aplicación
    app = QApplication(sys.argv)
    window = SqlmapAutoGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()