# SQLMap GUI Automator - Versión Final 🚀

Una interfaz gráfica moderna para SQLMap que permite automatizar pruebas de inyección SQL, con capacidades avanzadas de extracción de datos y descifrado de contraseñas.

## ✨ ¡Vista previa! ✨

_Ejemplo:_

![SQLMap GUI Automator Demo](https://i.ibb.co/n8tkQHHx/Screenshot-2025-05-12-133124.jpg)

---

## 🎯 Características Principales

-   🎨 **Interfaz gráfica moderna**: Tema oscuro elegante con acentos en color púrpura para una mejor experiencia visual.
-   🔍 **Detección de vulnerabilidades**: Visualización en tiempo real del proceso de escaneo de SQLMap.
-   📊 **Extracción interactiva de datos**: Navega y extrae fácilmente información de bases de datos vulnerables.
-   🔑 **Descifrado de contraseñas**: Utiliza los diccionarios integrados de SQLMap para intentar descifrar hashes.
-   ⚙️ **Opciones avanzadas**: Gran personalización de los escaneos para usuarios experimentados.

---

## 📋 Requisitos Previos

-   Python 3.6 o superior.
-   PySide6 (se intentará instalar automáticamente si no se encuentra).
-   SQLMap: **Este script debe ejecutarse desde el directorio raíz de SQLMap.**

---

## 🛠️ Instalación y Ejecución

1.  **Clona o descarga este repositorio** y coloca todos los archivos en el **directorio raíz de tu instalación de SQLMap**.
    ```bash
    # Ejemplo si tienes SQLMap en /opt/sqlmap y clonas este GUI dentro:
    # cd /opt/sqlmap
    # git clone [https://github.com/ByteCodeSecure/sqlmapproject-sqlmap-8fcd78f](https://github.com/ByteCodeSecure/sqlmapproject-sqlmap-8fcd78f)
    # mv sqlmap-gui-automator/* .
    # rm -rf sqlmap-gui-automator
    ```
    (Asegúrate de que el script principal y cualquier archivo auxiliar estén en la misma carpeta que `sqlmap.py`)

2.  **Ejecuta el script de inicio**:
    Desde el directorio raíz de SQLMap, ejecuta:
    ```bash
    ejecutar_sqlmap_gui.bat
    ```
    o si estás en Linux/macOS y creas un script `.sh`:
    ```bash
    chmod +x ejecutar_sqlmap_gui.sh
    ./ejecutar_sqlmap_gui.sh
    ```
---

## 📖 Guía de Uso

### 1. Escaneo de Vulnerabilidades
    - Abre la pestaña **"Escaneo"**.
    - Ingresa la **URL objetivo**.
    - Configura el **Nivel de Escaneo** (1-5) y **Riesgo** (1-3).
    - Opcionalmente, ajusta las **Opciones Avanzadas** según tus necesidades.
    - Haz clic en **"Iniciar Escaneo"**.
    - Observa el progreso y los resultados en tiempo real en la consola integrada.

### 2. Extracción de Datos
    - Una vez que SQLMap detecte una vulnerabilidad y tengas una sesión activa:
    - Ve a la pestaña **"Extracción"**.
    - Haz clic en **"Obtener bases de datos"** para listar las bases de datos accesibles.
    - Selecciona una base de datos del listado.
    - Haz clic en **"Obtener tablas"** para listar las tablas de la base de datos seleccionada.
    - Selecciona una tabla para ver sus columnas (se mostrarán automáticamente o con un botón tipo "Obtener Columnas").
    - Configura las opciones de extracción (ej. rango de filas, columnas específicas).
    - Haz clic en **"Extraer datos"**.
    - Si se detectan columnas con hashes de contraseñas, tendrás la opción de intentar descifrarlas usando los diccionarios de SQLMap.

### 3. Resultados
    - La pestaña **"Resultados"** (o la consola integrada) muestra la salida completa de SQLMap.
    - Puedes copiar el texto o exportarlo para un análisis posterior.

---

## ⚙️ Opciones Avanzadas Detalladas

Personaliza tus escaneos con una variedad de opciones avanzadas:

-   **Método de Request**: Elige el método HTTP (GET, POST, PUT, etc.).
-   **Datos POST**: Especifica los datos para enviar en solicitudes POST (`param1=valor1&param2=valor2`).
-   **Cookies**: Configura las cookies para la sesión (`nombre_cookie=valor_cookie; otra_cookie=otro_valor`).
-   **Proxy**: Define un proxy para enrutar el tráfico (ej. `http://127.0.0.1:8080`). Soporte para autenticación de proxy.
-   **User-Agent**: Utiliza un User-Agent aleatorio o especifica uno personalizado.
-   **Técnicas de Inyección**: Selecciona las técnicas de inyección SQL específicas a probar (B: Boolean-based blind, E: Error-based, U: Union query-based, S: Stacked queries, T: Time-based blind, Q: Inline queries).
-   **Técnicas de Evasión (Tamper Scripts)**: Utiliza scripts de `tamper` para ofuscar los payloads y evadir WAFs/IPSs.

---

## ✅ Mejoras y Correcciones Implementadas

Esta versión incluye mejoras significativas y correcciones de errores para una experiencia más fluida y efectiva:

-   **Extracción de Bases de Datos**: Patrón de detección robustecido para interpretar correctamente la salida de SQLMap, incluso con formatos variables.
-   **Extracción de Tablas y Columnas**: Optimización de los patrones de expresiones regulares para una identificación precisa de tablas y columnas.
-   **Manejo de Errores**: Implementación de un manejo de errores más detallado y visualización clara de mensajes para el usuario, facilitando la depuración.

---

## ⚠️ Uso Ético y Responsable

Esta herramienta está diseñada con fines **educativos y de investigación en seguridad**.
**Úsala exclusivamente en sistemas y redes para los que tengas autorización explícita y por escrito.**
El uso no autorizado de herramientas de pentesting como SQLMap y esta GUI en sistemas ajenos es **ilegal** y puede tener consecuencias graves.
Los desarrolladores de esta GUI no se hacen responsables del mal uso de esta herramienta.

---

## 📄 Licencia

Este proyecto se distribuye bajo la Licencia [NOMBRE DE LA LICENCIA AQUÍ, ej. MIT, GPLv3].
Consulta el archivo `LICENSE` para más detalles. (Asegúrate de añadir un archivo `LICENSE` a tu repositorio).

¡Esperamos que esta herramienta te sea útil!