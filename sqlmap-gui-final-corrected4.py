# Pestaña de escaneo
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