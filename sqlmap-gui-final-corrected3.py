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