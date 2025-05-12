#!/usr/bin/env python3

"""
SQLMap GUI Automator - Versión Final Corregida
Una interfaz gráfica para SQLMap con capacidades de extracción de datos
"""

#!/usr/bin/env python3

"""
SQLMap GUI Automator - Versión Final Corregida
Una interfaz gráfica para SQLMap con capacidades de extracción de datos
"""

import sys
import os
import subprocess
import threading
import time
import re
from datetime import datetime
from pathlib import Path

try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                                QTextEdit, QTabWidget, QComboBox, QCheckBox, 
                                QGroupBox, QSpinBox, QFileDialog, QMessageBox,
                                QProgressBar, QFormLayout, QListWidget)
    from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
    from PySide6.QtGui import QPalette, QColor, QFont, QTextCursor
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("PySide6 no está instalado. Instalando...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PySide6'])
        print("PySide6 instalado correctamente. Reiniciando aplicación...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except:
        print("Error al instalar PySide6. Por favor, instálalo manualmente con: pip install PySide6")
        sys.exit(1)

# Colores y estilos
COLORS = {
    'bg_primary': '#121212',
    'bg_secondary': '#1e1e1e',
    'bg_tertiary': '#2d2d2d',
    'bg_card': '#252525',
    'text_primary': '#e0e0e0',
    'text_secondary': '#b0b0b0',
    'text_muted': '#808080',
    'accent_primary': '#6a1b9a',
    'accent_secondary': '#9c27b0',
    'accent_hover': '#8e24aa',
    'accent_light': 'rgba(156, 39, 176, 0.1)',
    'success_color': '#2e7d32',
    'success_light': 'rgba(46, 125, 50, 0.1)',
    'warning_color': '#ff9800',
    'warning_light': 'rgba(255, 152, 0, 0.1)',
    'danger_color': '#c62828',
    'danger_light': 'rgba(198, 40, 40, 0.1)',
    'info_color': '#0288d1',
    'info_light': 'rgba(2, 136, 209, 0.1)',
    'border_color': '#424242',
}

# Clase para ejecutar SQLMap en un hilo separado
class SqlmapThread(QThread):
    output_ready = Signal(str)
    progress_update = Signal(int, int)  # current, total
    scan_complete = Signal(bool, str)  # success, message
    
    def __init__(self, options):
        super().__init__()
        self.options = options
        self.process = None
        self.output_file = None
        self.is_running = False
        
    def run(self):
        self.is_running = True
        
        # Crear archivo temporal para la salida
        import tempfile
        self.output_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.txt')
        output_path = self.output_file.name
        self.output_file.close()
        
        # Construir el comando
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "sqlmap.py")]
        
        # Manejar correctamente los parámetros especiales
        for key, value in self.options.items():
            if key == 'D':  # Base de datos
                cmd.extend(["-D", str(value)])
            elif key == 'T':  # Tabla
                cmd.extend(["-T", str(value)])
            elif key == 'C':  # Columnas
                cmd.extend(["-C", str(value)])
            elif key == 'start':  # Inicio del rango
                # Asegurar que el valor de start sea al menos 1
                start_value = max(1, int(value))
                cmd.extend(["--start", str(start_value)])
            elif key == 'stop':  # Fin del rango
                cmd.extend(["--stop", str(value)])
            elif value is True:
                cmd.append(f"--{key}")
            elif value not in (False, None, ""):
                cmd.append(f"--{key}={value}")
        
        # Añadir verbosidad
        cmd.extend(["-v", "3"])
        
        # Ejecutar el proceso
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Leer la salida línea por línea
            with open(output_path, 'w', encoding='utf-8') as f:
                for line in self.process.stdout:
                    f.write(line)
                    f.flush()
                    self.output_ready.emit(line.strip())
                    
                    # Buscar información de progreso
                    if '[' in line and '/' in line and ']' in line:
                        match = re.search(r'\[(\d+)/(\d+)\]', line)
                        if match:
                            current = int(match.group(1))
                            total = int(match.group(2))
                            self.progress_update.emit(current, total)
            
            # Esperar a que termine el proceso
            self.process.wait()
            
            # Leer el archivo de salida completo
            with open(output_path, 'r', encoding='utf-8') as f:
                full_output = f.read()
            
            # Determinar si fue exitoso
            success = False
            message = "Escaneo completado"
            
            if "sqlmap identified the following injection point" in full_output:
                success = True
                message = "¡Vulnerabilidad detectada!"
            elif "all tested parameters do not appear to be injectable" in full_output:
                success = False
                message = "No se detectaron vulnerabilidades"
            elif "unable to connect to the target URL" in full_output:
                success = False
                message = "Error de conexión: No se pudo conectar a la URL objetivo"
            
            self.scan_complete.emit(success, message)
            
        except Exception as e:
            self.output_ready.emit(f"Error: {str(e)}")
            self.scan_complete.emit(False, f"Error: {str(e)}")
        
        self.is_running = False
    
    def stop(self):
        if self.process and self.is_running:
            self.process.terminate()
            self.is_running = False

# Clase para ejecutar extracción de datos en un hilo separado
class SqlmapExtractionThread(QThread):
    output_ready = Signal(str)
    extraction_complete = Signal(bool, str, str)  # success, message, data
    
    def __init__(self, options):
        super().__init__()
        self.options = options
        self.process = None
        self.output_file = None
        self.is_running = False
        
    def run(self):
        self.is_running = True
        
        # Crear archivo temporal para la salida
        import tempfile
        self.output_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.txt')
        output_path = self.output_file.name
        self.output_file.close()
        
        # Construir el comando
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "sqlmap.py")]
        
        # Manejar correctamente los parámetros especiales
        for key, value in self.options.items():
            if key == 'D':  # Base de datos
                cmd.extend(["-D", str(value)])
            elif key == 'T':  # Tabla
                cmd.extend(["-T", str(value)])
            elif key == 'C':  # Columnas
                cmd.extend(["-C", str(value)])
            elif key == 'start':  # Inicio del rango
                # Asegurar que el valor de start sea al menos 1
                start_value = max(1, int(value))
                cmd.extend(["--start", str(start_value)])
            elif key == 'stop':  # Fin del rango
                cmd.extend(["--stop", str(value)])
            elif value is True:
                cmd.append(f"--{key}")
            elif value not in (False, None, ""):
                cmd.append(f"--{key}={value}")
        
        # Añadir verbosidad
        cmd.extend(["-v", "3"])
        
        # Ejecutar el proceso
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Leer la salida línea por línea
            with open(output_path, 'w', encoding='utf-8') as f:
                for line in self.process.stdout:
                    f.write(line)
                    f.flush()
                    self.output_ready.emit(line.strip())
            
            # Esperar a que termine el proceso
            self.process.wait()
            
            # Leer el archivo de salida completo
            with open(output_path, 'r', encoding='utf-8') as f:
                full_output = f.read()
            
            # Determinar si fue exitoso
            success = True
            message = "Extracción completada"
            
            if "unable to connect to the target URL" in full_output:
                success = False
                message = "Error de conexión: No se pudo conectar a la URL objetivo"
            
            self.extraction_complete.emit(success, message, full_output)
            
        except Exception as e:
            self.output_ready.emit(f"Error: {str(e)}")
            self.extraction_complete.emit(False, f"Error: {str(e)}", "")
        
        self.is_running = False
    
    def stop(self):
        if self.process and self.is_running:
            self.process.terminate()
            self.is_running = False

class ExtractionTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
        # Variables de estado
        self.current_url = ""
        self.current_db = ""
        self.current_table = ""
        self.databases = []
        self.tables = {}
        self.columns = {}
        self.extraction_thread = None
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Sección de bases de datos
        self.db_group = QGroupBox("Bases de datos")
        db_layout = QVBoxLayout(self.db_group)
        
        self.db_list = QListWidget()
        self.db_list.itemClicked.connect(self.on_database_selected)
        db_layout.addWidget(self.db_list)
        
        db_buttons = QHBoxLayout()
        self.get_dbs_button = QPushButton("Obtener bases de datos")
        self.get_dbs_button.clicked.connect(self.get_databases)
        db_buttons.addWidget(self.get_dbs_button)
        db_layout.addLayout(db_buttons)
        
        layout.addWidget(self.db_group)
        
        # Sección de tablas
        self.tables_group = QGroupBox("Tablas")
        tables_layout = QVBoxLayout(self.tables_group)
        
        self.tables_list = QListWidget()
        self.tables_list.itemClicked.connect(self.on_table_selected)
        tables_layout.addWidget(self.tables_list)
        
        tables_buttons = QHBoxLayout()
        self.get_tables_button = QPushButton("Obtener tablas")
        self.get_tables_button.clicked.connect(self.get_tables)
        self.get_tables_button.setEnabled(False)
        tables_buttons.addWidget(self.get_tables_button)
        tables_layout.addLayout(tables_buttons)
        
        layout.addWidget(self.tables_group)
        
        # Sección de datos
        self.data_group = QGroupBox("Datos")
        data_layout = QVBoxLayout(self.data_group)
        
        # Opciones de extracción
        options_form = QFormLayout()
        
        self.columns_input = QLineEdit()
        self.columns_input.setPlaceholderText("Todas las columnas (dejar en blanco) o separadas por comas")
        options_form.addRow("Columnas:", self.columns_input)
        
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 1000)
        self.limit_spin.setValue(100)
        options_form.addRow("Límite de filas:", self.limit_spin)
        
        data_layout.addLayout(options_form)
        
        # Botones de extracción
        data_buttons = QHBoxLayout()
        self.dump_button = QPushButton("Extraer datos")
        self.dump_button.clicked.connect(self.dump_data)
        self.dump_button.setEnabled(False)
        data_buttons.addWidget(self.dump_button)
        
        self.crack_button = QPushButton("Descifrar contraseñas")
        self.crack_button.clicked.connect(self.crack_passwords)
        self.crack_button.setEnabled(False)
        data_buttons.addWidget(self.crack_button)
        
        data_layout.addLayout(data_buttons)
        
        # Área de resultados
        self.data_text = QTextEdit()
        self.data_text.setReadOnly(True)
        data_layout.addWidget(self.data_text)
        
        # Botón de exportación
        export_button = QPushButton("Exportar datos")
        export_button.clicked.connect(self.export_data)
        data_layout.addWidget(export_button)
        
        layout.addWidget(self.data_group)
        
    def set_url(self, url):
        self.current_url = url
        self.get_dbs_button.setEnabled(bool(url))
        
    def get_databases(self, url=None):
        if url:
            self.current_url = url
            
        if not self.current_url:
            QMessageBox.warning(self, "Error", "No hay una URL objetivo definida.")
            return
            
        # Configurar opciones
        options = {
            'url': self.current_url,
            'batch': True,
            'dbs': True,
            'random-agent': True,
        }
        
        # Limpiar listas
        self.db_list.clear()
        self.tables_list.clear()
        self.data_text.clear()
        
        # Deshabilitar botones
        self.get_dbs_button.setEnabled(False)
        self.get_tables_button.setEnabled(False)
        self.dump_button.setEnabled(False)
        self.crack_button.setEnabled(False)
        
        # Mostrar mensaje
        self.data_text.append("Obteniendo bases de datos...")
        
        # Iniciar el hilo de extracción
        self.extraction_thread = SqlmapExtractionThread(options)
        self.extraction_thread.output_ready.connect(self.update_output)
        self.extraction_thread.extraction_complete.connect(self.databases_completed)
        self.extraction_thread.start()
        
    def databases_completed(self, success, message, output):
        # Habilitar botón
        self.get_dbs_button.setEnabled(True)
        
        if success:
            # Extraer bases de datos
            self.databases = self.extract_databases(output)
            
            if self.databases:
                # Actualizar lista de bases de datos
                self.db_list.clear()
                for db in self.databases:
                    self.db_list.addItem(db)
                
                # Mostrar mensaje
                self.data_text.append(f"Se encontraron {len(self.databases)} bases de datos.")
            else:
                self.data_text.append("No se pudieron extraer las bases de datos.")
        else:
            self.data_text.append(f"Error: {message}")
            
    def extract_databases(self, output):
        databases = []
        
        # Nuevo patrón para detectar bases de datos
        pattern = r"\[\*\] ([^\n\r]+)"
        matches = re.findall(pattern, output)
        
        # Filtrar resultados que no son bases de datos
        for match in matches:
            # Ignorar líneas que contienen "starting" o "ending"
            if "starting" not in match.lower() and "ending" not in match.lower():
                databases.append(match.strip())
        
        return databases
        
    def on_database_selected(self, item):
        self.current_db = item.text()
        self.get_tables_button.setEnabled(True)
        self.tables_list.clear()
        self.data_text.clear()
        self.data_text.append(f"Base de datos seleccionada: {self.current_db}")
        
    def get_tables(self):
        if not self.current_db:
            return
            
        # Configurar opciones
        options = {
            'url': self.current_url,
            'batch': True,
            'tables': True,
            # Usar D para la base de datos (forma abreviada)
            'D': self.current_db,
            'random-agent': True,
        }
        
        # Deshabilitar botones
        self.get_tables_button.setEnabled(False)
        self.dump_button.setEnabled(False)
        self.crack_button.setEnabled(False)
        
        # Mostrar mensaje
        self.data_text.append(f"Obteniendo tablas de {self.current_db}...")
        
        # Iniciar el hilo de extracción
        self.extraction_thread = SqlmapExtractionThread(options)
        self.extraction_thread.output_ready.connect(self.update_output)
        self.extraction_thread.extraction_complete.connect(self.tables_completed)
        self.extraction_thread.start()
        
    def tables_completed(self, success, message, output):
        # Habilitar botón
        self.get_tables_button.setEnabled(True)
        
        if success:
            # Extraer tablas
            tables = self.extract_tables(output, self.current_db)
            
            if tables:
                # Guardar tablas
                self.tables[self.current_db] = tables
                
                # Actualizar lista de tablas
                self.tables_list.clear()
                for table in tables:
                    self.tables_list.addItem(table)
                
                # Mostrar mensaje
                self.data_text.append(f"Se encontraron {len(tables)} tablas en {self.current_db}.")
            else:
                self.data_text.append("No se pudieron extraer las tablas.")
        else:
            self.data_text.append(f"Error: {message}")
            
    def extract_tables(self, output, db_name):
        tables = []
        
        # Buscar la sección de tablas
        pattern = r"\|\s+([^\s|]+)\s+\|"
        matches = re.findall(pattern, output)
        
        # Filtrar resultados que no son tablas
        for match in matches:
            # Ignorar nombres que parecen ser encabezados o separadores
            if not match.startswith('+') and not match.startswith('-'):
                tables.append(match.strip())
        
        return tables
        
    def on_table_selected(self, item):
        self.current_table = item.text()
        self.dump_button.setEnabled(True)
        self.data_text.clear()
        self.data_text.append(f"Tabla seleccionada: {self.current_table}")
        
        # Verificar si la tabla podría contener contraseñas
        password_columns = ['password', 'pass', 'passwd', 'pwd', 'hash', 'contraseña', 'clave']
        
        # Obtener columnas de la tabla
        self.get_columns()
        
    def get_columns(self):
        if not self.current_db or not self.current_table:
            return
            
        # Configurar opciones
        options = {
            'url': self.current_url,
            'batch': True,
            'columns': True,
            # Usar D para la base de datos (forma abreviada)
            'D': self.current_db,
            # Usar T para la tabla (forma abreviada)
            'T': self.current_table,
            'random-agent': True,
        }
        
        # Mostrar mensaje
        self.data_text.append(f"Obteniendo columnas de {self.current_table}...")
        
        # Iniciar el hilo de extracción
        self.extraction_thread = SqlmapExtractionThread(options)
        self.extraction_thread.output_ready.connect(self.update_output)
        self.extraction_thread.extraction_complete.connect(self.columns_completed)
        self.extraction_thread.start()
        
    def columns_completed(self, success, message, output):
        if success:
            # Extraer columnas
            columns = self.extract_columns(output, self.current_db, self.current_table)
            
            if columns:
                # Guardar columnas
                self.columns[(self.current_db, self.current_table)] = columns
                
                # Mostrar columnas
                self.data_text.append(f"Columnas en {self.current_table}:")
                for column, column_type in columns:
                    self.data_text.append(f"  - {column} ({column_type})")
                
                # Verificar si hay columnas de contraseñas
                password_columns = ['password', 'pass', 'passwd', 'pwd', 'hash', 'contraseña', 'clave']
                has_password = any(any(pwd_col in col.lower() for pwd_col in password_columns) for col, _ in columns)
                
                # Habilitar/deshabilitar botón de descifrado
                self.crack_button.setEnabled(has_password)
            else:
                self.data_text.append("No se pudieron extraer las columnas.")
                self.crack_button.setEnabled(False)
        else:
            self.data_text.append(f"Error: {message}")
            self.crack_button.setEnabled(False)
            
    def extract_columns(self, output, db_name, table_name):
        columns = []
        
        # Buscar la sección de columnas
        pattern = r"\|\s+([^\s|]+)\s+\|\s+([^\s|]+)\s+\|"
        matches = re.findall(pattern, output)
        
        # Filtrar resultados que no son columnas
        for match in matches:
            # Ignorar nombres que parecen ser encabezados o separadores
            if not match[0].startswith('+') and not match[0].startswith('-'):
                columns.append((match[0].strip(), match[1].strip()))
        
        return columns

    def dump_data(self):
        if not self.current_db or not self.current_table:
            return
            
        # Configurar opciones
        options = {
            'url': self.current_url,
            'batch': True,
            'dump': True,
            # Usar D para la base de datos (forma abreviada)
            'D': self.current_db,
            # Usar T para la tabla (forma abreviada)
            'T': self.current_table,
            'random-agent': True,
        }
        
        # Añadir límite si está especificado
        if self.limit_spin.value() > 0:
            # Usar los parámetros correctos para el límite
            options['start'] = 1  # El valor de start debe ser mayor que cero (corregido)
            options['stop'] = self.limit_spin.value()
            
        # Añadir columnas si están especificadas
        if self.columns_input.text().strip():
            # Usar C para las columnas (forma abreviada)
            options['C'] = self.columns_input.text().strip()
            
        # Deshabilitar botones
        self.dump_button.setEnabled(False)
        
        # Mostrar mensaje
        self.data_text.clear()
        self.data_text.append(f"Extrayendo datos de {self.current_table}...")
        
        # Iniciar el hilo de extracción
        self.extraction_thread = SqlmapExtractionThread(options)
        self.extraction_thread.output_ready.connect(self.update_output)
        self.extraction_thread.extraction_complete.connect(self.dump_completed)
        self.extraction_thread.start()
        
    def dump_completed(self, success, message, output):
        # Habilitar botón
        self.dump_button.setEnabled(True)
        
        if success:
            # Extraer datos
            dump_data = self.extract_dump_data(output)
            
            # Mostrar datos
            self.data_text.clear()
            self.data_text.append(dump_data)
            
            # Verificar si hay columnas de contraseñas
            if self.columns.get((self.current_db, self.current_table)):
                password_columns = ['password', 'pass', 'passwd', 'pwd', 'hash', 'contraseña', 'clave']
                has_password = any(any(pwd_col in col.lower() for pwd_col in password_columns) for col, _ in self.columns[(self.current_db, self.current_table)])
                
                # Habilitar/deshabilitar botón de descifrado
                self.crack_button.setEnabled(has_password)
        else:
            self.data_text.append(f"Error: {message}")
            
    def extract_dump_data(self, output):
        # Buscar la sección de datos
        pattern = rf"Database: {re.escape(self.current_db)}.*?Table: {re.escape(self.current_table)}"
        match = re.search(pattern, output, re.DOTALL)
        
        if match:
            # Extraer la sección de datos
            data_section = output[match.start():]
            # Limitar a la siguiente sección importante
            next_section = re.search(r"\[\*\]", data_section[1:])
            if next_section:
                data_section = data_section[:next_section.start() + 1]
                
            return data_section
        else:
            return "No se pudieron extraer los datos."
            
    def crack_passwords(self):
        if not self.current_db or not self.current_table:
            return
            
        # Verificar si hay columnas de contraseñas
        if not self.columns.get((self.current_db, self.current_table)):
            self.data_text.append("No hay información de columnas disponible.")
            return
            
        password_columns = ['password', 'pass', 'passwd', 'pwd', 'hash', 'contraseña', 'clave']
        pwd_cols = [col for col, _ in self.columns[(self.current_db, self.current_table)] 
                   if any(pwd_col in col.lower() for pwd_col in password_columns)]
        
        if not pwd_cols:
            self.data_text.append("No se detectaron columnas de contraseñas.")
            return
            
        # Seleccionar columna de contraseña
        pwd_col = pwd_cols[0]
        
        # Configurar opciones
        options = {
            'url': self.current_url,
            'batch': True,
            'dump': True,
            # Usar D para la base de datos (forma abreviada)
            'D': self.current_db,
            # Usar T para la tabla (forma abreviada)
            'T': self.current_table,
            # Usar C para las columnas (forma abreviada)
            'C': pwd_col,
            'crack': True,
            'random-agent': True,
        }
        
        # Deshabilitar botones
        self.crack_button.setEnabled(False)
        
        # Mostrar mensaje
        self.data_text.clear()
        self.data_text.append(f"Intentando descifrar contraseñas en la columna {pwd_col}...")
        
        # Iniciar el hilo de extracción
        self.extraction_thread = SqlmapExtractionThread(options)
        self.extraction_thread.output_ready.connect(self.update_output)
        self.extraction_thread.extraction_complete.connect(self.crack_completed)
        self.extraction_thread.start()
        
    def crack_completed(self, success, message, output):
        # Habilitar botón
        self.crack_button.setEnabled(True)
        
        if success:
            # Extraer resultados del descifrado
            crack_data = self.extract_crack_data(output)
            
            # Mostrar datos
            self.data_text.clear()
            self.data_text.append(crack_data)
        else:
            self.data_text.append(f"Error: {message}")
            
    def extract_crack_data(self, output):
        # Buscar la sección de descifrado
        pattern = r"cracked password hashes \(.*?\):(.*?)(?:\[\*\]|\Z)"
        match = re.search(pattern, output, re.DOTALL | re.IGNORECASE)
        
        if match:
            return f"Resultados del descifrado de contraseñas:\n\n{match.group(1).strip()}"
        else:
            return "No se encontraron resultados de descifrado de contraseñas."
            
    def export_data(self):
        data = self.data_text.toPlainText()
        if not data:
            QMessageBox.warning(self, "Error", "No hay datos para exportar.")
            return
            
        # Mostrar diálogo para guardar archivo
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar datos", 
            f"{self.current_db}_{self.current_table}.txt" if self.current_db and self.current_table else "sqlmap_data.txt", 
            "Archivos de texto (*.txt);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(data)
                QMessageBox.information(self, "Éxito", "Datos exportados correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar datos: {str(e)}")
                
    def update_output(self, line):
        # Actualizar la salida en tiempo real
        self.data_text.append(line)
        
        # Desplazar al final
        cursor = self.data_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.data_text.setTextCursor(cursor)
        
        # Actualizar la salida en la pestaña de resultados
        if hasattr(self.parent, 'results_tab'):
            self.parent.results_tab.update_output(line)

# Pestaña de resultados
class ResultsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Resumen
        summary_group = QGroupBox("Resumen del escaneo")
        summary_layout = QFormLayout(summary_group)
        
        self.summary_url = QLabel("")
        summary_layout.addRow("URL escaneada:", self.summary_url)
        
        self.summary_status = QLabel("")
        summary_layout.addRow("Estado:", self.summary_status)
        
        self.summary_time = QLabel("")
        summary_layout.addRow("Tiempo de escaneo:", self.summary_time)
        
        layout.addWidget(summary_group)
        
        # Salida completa
        output_group = QGroupBox("Salida completa")
        output_layout = QVBoxLayout(output_group)
        
        output_buttons = QHBoxLayout()
        copy_button = QPushButton("Copiar")
        copy_button.clicked.connect(self.copy_output)
        export_button = QPushButton("Exportar")
        export_button.clicked.connect(self.export_output)
        output_buttons.addWidget(copy_button)
        output_buttons.addWidget(export_button)
        output_layout.addLayout(output_buttons)
        
        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)
        output_layout.addWidget(self.results_output)
        
        layout.addWidget(output_group)
        
    def update_output(self, line):
        self.results_output.append(line)
        
        # Desplazar al final
        cursor = self.results_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.results_output.setTextCursor(cursor)
        
        # Actualizar resumen
        if hasattr(self.parent, 'scan_tab'):
            if hasattr(self.parent.scan_tab, 'details_url'):
                self.summary_url.setText(self.parent.scan_tab.details_url.text())
            if hasattr(self.parent.scan_tab, 'details_status'):
                self.summary_status.setText(self.parent.scan_tab.details_status.text())
            if hasattr(self.parent.scan_tab, 'details_time'):
                self.summary_time.setText(self.parent.scan_tab.details_time.text())
        
    def copy_output(self):
        text = self.results_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copiado", "Resultados copiados al portapapeles")
        else:
            QMessageBox.warning(self, "Error", "No hay resultados para copiar.")
            
    def export_output(self):
        text = self.results_output.toPlainText()
        if not text:
            QMessageBox.warning(self, "Error", "No hay resultados para exportar.")
            return
            
        # Mostrar diálogo para guardar archivo
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar resultados", 
            f"sqlmap_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 
            "Archivos de texto (*.txt);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "Éxito", "Resultados exportados correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar resultados: {str(e)}")

# Pestaña de ayuda
class HelpTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>SQLMap GUI Automator</h2>
        <p>Una interfaz gráfica para SQLMap que permite automatizar pruebas de inyección SQL.</p>
        
        <h3>Instrucciones de uso:</h3>
        <ol>
            <li><strong>Escaneo:</strong> Ingresa la URL objetivo que deseas analizar. Esta debe contener parámetros (como ?id=1).</li>
            <li><strong>Extracción:</strong> Una vez detectada una vulnerabilidad, puedes extraer bases de datos, tablas y datos.</li>
            <li><strong>Resultados:</strong> Revisa la salida completa y exporta los resultados para su análisis posterior.</li>
        </ol>
        
        <h3>Extracción de datos:</h3>
        <ol>
            <li>Después de un escaneo exitoso, ve a la pestaña de Extracción.</li>
            <li>Haz clic en "Obtener bases de datos" para ver las bases de datos disponibles.</li>
            <li>Selecciona una base de datos y haz clic en "Obtener tablas".</li>
            <li>Selecciona una tabla y configura las opciones de extracción.</li>
            <li>Haz clic en "Extraer datos" para obtener los datos de la tabla.</li>
            <li>Si se detectan columnas de contraseñas, puedes intentar descifrarlas con el botón "Descifrar contraseñas".</li>
        </ol>
        
        <h3>Opciones avanzadas:</h3>
        <ul>
            <li><strong>Método:</strong> Selecciona el método HTTP (GET, POST, etc.).</li>
            <li><strong>Datos POST:</strong> Especifica los datos para solicitudes POST.</li>
            <li><strong>Cookies:</strong> Configura cookies para la solicitud.</li>
            <li><strong>Proxy:</strong> Usa un proxy para las solicitudes, con o sin autenticación.</li>
            <li><strong>User-Agent:</strong> Usa un User-Agent aleatorio o personalizado.</li>
            <li><strong>Técnicas de inyección:</strong> Selecciona qué técnicas utilizar.</li>
            <li><strong>Técnicas de evasión:</strong> Usa técnicas de tamper para evadir protecciones WAF/IPS.</li>
        </ul>
        
        <h3>Uso ético:</h3>
        <p>Esta herramienta debe usarse únicamente con fines educativos y en sistemas para los que tengas autorización explícita. El uso no autorizado de esta herramienta puede ser ilegal.</p>
        """)
        layout.addWidget(help_text)

class ScanTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
        # Variables de estado
        self.sqlmap_thread = None
        self.scan_start_time = None
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.update_scan_time)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulario de escaneo
        self.scan_form = QWidget()
        form_layout = QFormLayout(self.scan_form)
        
        # URL objetivo
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://ejemplo.com/pagina.php?id=1")
        form_layout.addRow("URL Objetivo:", self.url_input)
        
        # Escanear formularios
        self.scan_forms_check = QCheckBox("Escanear formularios en la página")
        form_layout.addRow("", self.scan_forms_check)
        
        # Nivel y riesgo
        level_risk_layout = QHBoxLayout()
        
        level_layout = QVBoxLayout()
        level_label = QLabel("Nivel de escaneo:")
        self.level_combo = QComboBox()
        self.level_combo.addItems(["1 - Rápido (recomendado)", "2 - Medio", "3 - Profundo", "5 - Exhaustivo"])
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_combo)
        
        risk_layout = QVBoxLayout()
        risk_label = QLabel("Nivel de riesgo:")
        self.risk_combo = QComboBox()
        self.risk_combo.addItems(["1 - Bajo (recomendado)", "2 - Medio", "3 - Alto"])
        risk_layout.addWidget(risk_label)
        risk_layout.addWidget(self.risk_combo)
        
        level_risk_layout.addLayout(level_layout)
        level_risk_layout.addLayout(risk_layout)
        form_layout.addRow("", level_risk_layout)
        
        # Opciones avanzadas
        self.advanced_check = QCheckBox("Mostrar opciones avanzadas")
        self.advanced_check.toggled.connect(self.toggle_advanced_options)
        form_layout.addRow("", self.advanced_check)
        
        # Contenedor de opciones avanzadas
        self.advanced_options = QWidget()
        self.advanced_options.setVisible(False)
        advanced_layout = QVBoxLayout(self.advanced_options)
        
        # Método de request
        method_layout = QHBoxLayout()
        method_label = QLabel("Método de Request:")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"])
        self.method_combo.currentTextChanged.connect(self.on_method_changed)
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        advanced_layout.addLayout(method_layout)
        
        # Datos POST
        post_layout = QHBoxLayout()
        post_label = QLabel("Datos POST:")
        self.post_input = QLineEdit()
        self.post_input.setPlaceholderText("param1=value1&param2=value2")
        post_layout.addWidget(post_label)
        post_layout.addWidget(self.post_input)
        advanced_layout.addLayout(post_layout)
        
        # Cookies
        cookies_layout = QHBoxLayout()
        cookies_label = QLabel("Cookies:")
        self.cookies_input = QLineEdit()
        self.cookies_input.setPlaceholderText("cookie1=value1; cookie2=value2")
        cookies_layout.addWidget(cookies_label)
        cookies_layout.addWidget(self.cookies_input)
        advanced_layout.addLayout(cookies_layout)
        
        # Proxy
        proxy_group = QGroupBox("Configuración de Proxy")
        proxy_layout = QFormLayout(proxy_group)
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://proxy:puerto")
        proxy_layout.addRow("Dirección del Proxy:", self.proxy_input)
        
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "HTTPS", "SOCKS4", "SOCKS5"])
        proxy_layout.addRow("Tipo de Proxy:", self.proxy_type_combo)
        
        proxy_auth_layout = QHBoxLayout()
        self.proxy_user = QLineEdit()
        self.proxy_user.setPlaceholderText("usuario")
        self.proxy_pass = QLineEdit()
        self.proxy_pass.setPlaceholderText("contraseña")
        self.proxy_pass.setEchoMode(QLineEdit.Password)
        proxy_auth_layout.addWidget(self.proxy_user)
        proxy_auth_layout.addWidget(self.proxy_pass)
        proxy_layout.addRow("Credenciales:", proxy_auth_layout)
        
        advanced_layout.addWidget(proxy_group)
        
        # User-Agent
        ua_group = QGroupBox("User-Agent")
        ua_layout = QVBoxLayout(ua_group)
        
        self.random_ua_check = QCheckBox("Usar User-Agent aleatorio")
        self.random_ua_check.setChecked(True)
        self.random_ua_check.toggled.connect(self.toggle_user_agent)
        ua_layout.addWidget(self.random_ua_check)
        
        self.user_agent_input = QLineEdit()
        self.user_agent_input.setPlaceholderText("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...")
        self.user_agent_input.setEnabled(False)
        ua_layout.addWidget(self.user_agent_input)
        
        advanced_layout.addWidget(ua_group)
        
        # Técnicas de inyección
        techniques_group = QGroupBox("Técnicas de inyección")
        techniques_layout = QVBoxLayout(techniques_group)
        
        self.tech_boolean = QCheckBox("Boolean-based blind")
        self.tech_boolean.setChecked(True)
        techniques_layout.addWidget(self.tech_boolean)
        
        self.tech_error = QCheckBox("Error-based")
        self.tech_error.setChecked(True)
        techniques_layout.addWidget(self.tech_error)
        
        self.tech_union = QCheckBox("Union query-based")
        self.tech_union.setChecked(True)
        techniques_layout.addWidget(self.tech_union)
        
        self.tech_stacked = QCheckBox("Stacked queries")
        techniques_layout.addWidget(self.tech_stacked)
        
        self.tech_time = QCheckBox("Time-based blind")
        self.tech_time.setChecked(True)
        techniques_layout.addWidget(self.tech_time)
        
        advanced_layout.addWidget(techniques_group)
        
        # Opciones adicionales
        options_group = QGroupBox("Opciones adicionales")
        options_layout = QVBoxLayout(options_group)
        
        self.tamper_check = QCheckBox("Usar técnicas de evasión (tamper)")
        options_layout.addWidget(self.tamper_check)
        
        self.skip_waf_check = QCheckBox("Intentar evadir WAF/IPS")
        options_layout.addWidget(self.skip_waf_check)
        
        self.force_ssl_check = QCheckBox("Forzar SSL/HTTPS")
        options_layout.addWidget(self.force_ssl_check)
        
        advanced_layout.addWidget(options_group)
        
        # DBMS
        dbms_layout = QHBoxLayout()
        dbms_label = QLabel("Base de datos objetivo:")
        self.dbms_combo = QComboBox()
        self.dbms_combo.addItems(["Auto-detectar", "MySQL", "PostgreSQL", "Microsoft SQL Server", "Oracle", "SQLite"])
        dbms_layout.addWidget(dbms_label)
        dbms_layout.addWidget(self.dbms_combo)
        advanced_layout.addLayout(dbms_layout)
        
        form_layout.addRow("", self.advanced_options)
        
        # Botón de inicio
        start_button = QPushButton("Iniciar Escaneo")
        start_button.setStyleSheet(f"background-color: {COLORS['accent_primary']}; color: white; font-weight: bold;")
        start_button.clicked.connect(self.start_scan)
        form_layout.addRow("", start_button)
        
        layout.addWidget(self.scan_form)
        
        # Visualización en tiempo real (inicialmente oculta)
        self.realtime_view = QWidget()
        self.realtime_view.setVisible(False)
        realtime_layout = QVBoxLayout(self.realtime_view)
        
        # Alerta de escaneo
        self.scan_alert = QLabel("Escaneando el objetivo en busca de vulnerabilidades...")
        self.scan_alert.setStyleSheet(f"padding: 10px; border-radius: 4px; background-color: {COLORS['info_light']}; color: {COLORS['info_color']};")
        realtime_layout.addWidget(self.scan_alert)
        
        # Barra de progreso
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {COLORS['accent_secondary']}; }}")
        self.progress_text = QLabel("0% Completado")
        self.progress_text.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_text)
        realtime_layout.addLayout(progress_layout)
        
        # Detalles del escaneo
        details_group = QGroupBox("Detalles del escaneo")
        details_layout = QFormLayout(details_group)
        
        self.details_url = QLabel("")
        details_layout.addRow("URL:", self.details_url)
        
        self.details_status = QLabel("En progreso")
        self.details_status.setStyleSheet(f"color: {COLORS['info_color']}; font-weight: bold;")
        details_layout.addRow("Estado:", self.details_status)
        
        self.details_time = QLabel("00:00")
        details_layout.addRow("Tiempo:", self.details_time)
        
        realtime_layout.addWidget(details_group)
        
        # Reporte de escaneo
        self.scan_report = QGroupBox("Reporte de escaneo")
        self.scan_report.setVisible(False)
        report_layout = QVBoxLayout(self.scan_report)
        
        self.report_header = QLabel("Vulnerabilidad detectada")
        self.report_header.setStyleSheet(f"padding: 10px; border-radius: 4px; background-color: {COLORS['success_light']}; color: {COLORS['success_color']}; font-weight: bold;")
        report_layout.addWidget(self.report_header)
        
        self.report_content = QLabel("")
        self.report_content.setWordWrap(True)
        report_layout.addWidget(self.report_content)
        
        self.injection_points = QTextEdit()
        self.injection_points.setReadOnly(True)
        self.injection_points.setMaximumHeight(150)
        report_layout.addWidget(self.injection_points)
        
        next_steps_layout = QHBoxLayout()
        self.get_dbs_button = QPushButton("Obtener bases de datos")
        self.get_dbs_button.setStyleSheet(f"background-color: {COLORS['accent_primary']}; color: white;")
        self.get_dbs_button.clicked.connect(self.get_databases)
        next_steps_layout.addWidget(self.get_dbs_button)
        report_layout.addLayout(next_steps_layout)
        
        realtime_layout.addWidget(self.scan_report)
        
        # Salida en tiempo real
        output_group = QGroupBox("Salida en tiempo real")
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(200)
        output_layout.addWidget(self.output_text)
        
        realtime_layout.addWidget(output_group)
        
        # Botones de control
        control_layout = QHBoxLayout()
        
        self.stop_button = QPushButton("Detener")
        self.stop_button.setStyleSheet(f"background-color: {COLORS['danger_color']}; color: white;")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.clicked.connect(self.reset_scan)
        control_layout.addWidget(self.reset_button)
        
        realtime_layout.addLayout(control_layout)
        
        layout.addWidget(self.realtime_view)
        
    def toggle_advanced_options(self, checked):
        self.advanced_options.setVisible(checked)
        
    def toggle_user_agent(self, checked):
        self.user_agent_input.setEnabled(not checked)
        
    def on_method_changed(self, method):
        # Habilitar/deshabilitar datos POST según el método
        is_post_like = method in ["POST", "PUT", "PATCH"]
        self.post_input.setEnabled(is_post_like)
        
    def start_scan(self):
        # Validar URL
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Por favor, ingresa una URL objetivo.")
            return
            
        if "?" not in url or "=" not in url:
            response = QMessageBox.question(
                self, 
                "Advertencia", 
                "La URL no parece contener parámetros (como ?id=1). SQLMap necesita parámetros para probar inyecciones SQL.\n\n¿Deseas continuar de todos modos?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if response == QMessageBox.No:
                return
        
        # Recopilar opciones
        options = {
            'url': url,
            'batch': True,
            'forms': self.scan_forms_check.isChecked(),
            'level': int(self.level_combo.currentText().split()[0]),
            'risk': int(self.risk_combo.currentText().split()[0]),
        }
        
        # Opciones avanzadas
        if self.advanced_check.isChecked():
            # Método de request
            options['method'] = self.method_combo.currentText()
            
            # Datos POST
            if self.post_input.isEnabled() and self.post_input.text().strip():
                options['data'] = self.post_input.text().strip()
                
            # Cookies
            if self.cookies_input.text().strip():
                options['cookie'] = self.cookies_input.text().strip()
                
            # Proxy
            if self.proxy_input.text().strip():
                options['proxy'] = self.proxy_input.text().strip()
                options['proxy-type'] = self.proxy_type_combo.currentText().lower()
                
                # Credenciales del proxy
                if self.proxy_user.text().strip() and self.proxy_pass.text().strip():
                    options['proxy-cred'] = f"{self.proxy_user.text().strip()}:{self.proxy_pass.text().strip()}"
            
            # User-Agent
            if self.random_ua_check.isChecked():
                options['random-agent'] = True
            elif self.user_agent_input.text().strip():
                options['user-agent'] = self.user_agent_input.text().strip()
                
            # Técnicas de inyección
            techniques = ""
            if self.tech_boolean.isChecked(): techniques += "B"
            if self.tech_error.isChecked(): techniques += "E"
            if self.tech_union.isChecked(): techniques += "U"
            if self.tech_stacked.isChecked(): techniques += "S"
            if self.tech_time.isChecked(): techniques += "T"
            
            if techniques:
                options['technique'] = techniques
                
            # Opciones adicionales
            if self.tamper_check.isChecked():
                options['tamper'] = "space2comment,between,randomcase"
                
            if self.skip_waf_check.isChecked():
                options['skip-waf'] = True
                
            if self.force_ssl_check.isChecked():
                options['force-ssl'] = True
                
            # DBMS
            if self.dbms_combo.currentIndex() > 0:
                options['dbms'] = self.dbms_combo.currentText().lower().replace(" ", "")
        else:
            # Siempre usar random-agent por defecto
            options['random-agent'] = True
            
        # Cambiar la interfaz
        self.scan_form.setVisible(False)
        self.realtime_view.setVisible(True)
        self.scan_report.setVisible(False)
        
        # Actualizar detalles
        self.details_url.setText(url)
        self.details_status.setText("En progreso")
        self.details_status.setStyleSheet(f"color: {COLORS['info_color']}; font-weight: bold;")
        self.details_time.setText("00:00")
        
        # Habilitar botón de detener
        self.stop_button.setEnabled(True)
        
        # Iniciar temporizador
        self.scan_start_time = time.time()
        self.scan_timer.start(1000)  # Actualizar cada segundo
        
        # Limpiar salida
        self.output_text.clear()
        
        # Iniciar el hilo de SQLMap
        self.sqlmap_thread = SqlmapThread(options)
        self.sqlmap_thread.output_ready.connect(self.update_output)
        self.sqlmap_thread.progress_update.connect(self.update_progress)
        self.sqlmap_thread.scan_complete.connect(self.scan_completed)
        self.sqlmap_thread.start()
        
        # Guardar URL para la pestaña de extracción
        if hasattr(self.parent, 'extraction_tab'):
            self.parent.extraction_tab.set_url(url)

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

