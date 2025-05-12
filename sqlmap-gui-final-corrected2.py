# Pestaña de extracción
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