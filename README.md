# SQLMap GUI Automator - Versión Final

Una interfaz gráfica moderna para SQLMap que permite automatizar pruebas de inyección SQL, con capacidades avanzadas de extracción de datos y descifrado de contraseñas.

## Características principales

- **Interfaz gráfica moderna** con tema oscuro y acentos en color púrpura
- **Detección de vulnerabilidades** con visualización en tiempo real
- **Extracción interactiva de datos** de bases de datos vulnerables
- **Descifrado de contraseñas** utilizando los diccionarios integrados de SQLMap
- **Opciones avanzadas** para personalizar los escaneos

## Requisitos

- Python 3.6 o superior
- PySide6 (se instalará automáticamente si es necesario)
- SQLMap (este script debe ejecutarse desde el directorio raíz de SQLMap)

## Instalación y ejecución

1. Coloca todos los archivos en el directorio raíz de SQLMap
2. Ejecuta el script: `ejecutar_sqlmap_gui.bat`

## Uso de la aplicación

### 1. Escaneo de vulnerabilidades

- Ingresa la URL objetivo en la pestaña de Escaneo
- Configura el nivel de escaneo y riesgo
- Opcionalmente, configura opciones avanzadas
- Haz clic en "Iniciar Escaneo"
- Observa el progreso en tiempo real

### 2. Extracción de datos

- Una vez detectada una vulnerabilidad, ve a la pestaña de Extracción
- Haz clic en "Obtener bases de datos" para ver las bases de datos disponibles
- Selecciona una base de datos y haz clic en "Obtener tablas"
- Selecciona una tabla para ver sus columnas
- Configura las opciones de extracción y haz clic en "Extraer datos"
- Si se detectan columnas de contraseñas, puedes intentar descifrarlas

### 3. Resultados

- La pestaña de Resultados muestra la salida completa de SQLMap
- Puedes copiar o exportar los resultados para su análisis posterior

## Opciones avanzadas

- **Método de Request**: Selecciona el método HTTP (GET, POST, etc.)
- **Datos POST**: Especifica los datos para solicitudes POST
- **Cookies**: Configura cookies para la solicitud
- **Proxy**: Usa un proxy para las solicitudes, con o sin autenticación
- **User-Agent**: Usa un User-Agent aleatorio o personalizado
- **Técnicas de inyección**: Selecciona qué técnicas utilizar
- **Técnicas de evasión**: Usa técnicas de tamper para evadir protecciones WAF/IPS

## Correcciones implementadas

Esta versión incluye correcciones para los siguientes problemas:

- **Extracción de bases de datos**: Se ha mejorado el patrón de detección para manejar correctamente el formato de salida de SQLMap.
- **Extracción de tablas y columnas**: Se han optimizado los patrones para detectar correctamente tablas y columnas.
- **Manejo de errores**: Se ha mejorado el manejo de errores y la visualización de mensajes.

## Uso ético

Esta herramienta debe usarse únicamente con fines educativos y en sistemas para los que tengas autorización explícita. El uso no autorizado de esta herramienta puede ser ilegal.