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