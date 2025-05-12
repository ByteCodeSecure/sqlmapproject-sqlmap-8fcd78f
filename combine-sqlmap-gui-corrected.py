#!/usr/bin/env python3

"""
Script para combinar los archivos de SQLMap GUI en un único archivo ejecutable
"""

import os
import sys

def combine_files():
    """Combina los archivos en un único archivo ejecutable"""
    # Verificar que los archivos existen
    files = [
        'sqlmap-gui-final-corrected.py',
        'sqlmap-gui-final-corrected2.py',
        'sqlmap-gui-final-corrected3.py',
        'sqlmap-gui-final-corrected4.py',
        'sqlmap-gui-final-corrected5.py'
    ]
    
    for file in files:
        if not os.path.exists(file):
            print(f"Error: No se encontró el archivo {file}")
            return False
    
    # Combinar los archivos
    try:
        with open('sqlmap-gui-corrected-final.py', 'w', encoding='utf-8') as outfile:
            # Escribir encabezado
            outfile.write('#!/usr/bin/env python3\n\n')
            outfile.write('"""\nSQLMap GUI Automator - Versión Final Corregida\nUna interfaz gráfica para SQLMap con capacidades de extracción de datos\n"""\n\n')
            
            # Escribir el contenido de cada archivo
            for file in files:
                with open(file, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    # Eliminar líneas de comentarios y espacios en blanco al principio
                    if file != files[0]:  # No eliminar del primer archivo
                        lines = content.split('\n')
                        start_line = 0
                        for i, line in enumerate(lines):
                            if line.strip() and not line.strip().startswith('#'):
                                start_line = i
                                break
                        content = '\n'.join(lines[start_line:])
                    outfile.write(content)
                    outfile.write('\n\n')
        
        # Hacer el archivo ejecutable
        os.chmod('sqlmap-gui-corrected-final.py', 0o755)
        
        print("Archivo combinado creado: sqlmap-gui-corrected-final.py")
        return True
    except Exception as e:
        print(f"Error al combinar archivos: {str(e)}")
        return False

if __name__ == "__main__":
    combine_files()