#!/usr/bin/env python3

"""
Script para corregir el problema de extracción de datos en SQLMap GUI
"""

import os
import re
import sys

def fix_files():
    """Corrige los archivos de SQLMap GUI para solucionar el problema de extracción de datos"""
    
    # Lista de archivos a corregir
    files = [
        'sqlmap-gui-final-corrected.py',
        'sqlmap-gui-final-corrected2.py',
        'sqlmap-gui-final-corrected3.py',
        'sqlmap-gui-final-corrected4.py',
        'sqlmap-gui-final-corrected5.py'
    ]
    
    # Patrones a buscar y reemplazar
    patterns = [
        # Corregir el valor de 'start' para que sea siempre mayor que cero
        (r"options\['start'\] = 0", "options['start'] = 1  # El valor de start debe ser mayor que cero"),
        
        # Asegurar que el parámetro start siempre sea mayor que cero
        (r"elif key == 'start':  # Inicio del rango\n                cmd.extend\(\[\"--start\", str\(value\)\]\)", 
         "elif key == 'start':  # Inicio del rango\n                # Asegurar que el valor de start sea al menos 1\n                start_value = max(1, int(value))\n                cmd.extend([\"--start\", str(start_value)])"),
    ]
    
    # Procesar cada archivo
    for file in files:
        if not os.path.exists(file):
            print(f"Advertencia: No se encontró el archivo {file}")
            continue
        
        # Leer el contenido del archivo
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aplicar los reemplazos
        modified = False
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
        
        # Guardar el archivo si se modificó
        if modified:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Archivo {file} corregido")
        else:
            print(f"No se encontraron problemas en {file}")
    
    # Recombinar los archivos
    print("Recombinando archivos...")
    os.system(f"{sys.executable} combine-sqlmap-gui-corrected.py")
    
    print("Corrección completada")

if __name__ == "__main__":
    fix_files()