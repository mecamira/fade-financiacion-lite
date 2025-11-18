#!/usr/bin/env python3
"""
Script para verificar que el código del scraper está actualizado
"""

import inspect
from utils.bdns_scraper import BDNSScraper

print("=" * 80)
print("VERIFICACIÓN DE VERSIÓN DEL SCRAPER")
print("=" * 80)

# Verificar que los métodos nuevos existen
scraper_methods = [method for method in dir(BDNSScraper) if not method.startswith('_')]
print("\nMétodos públicos del BDNSScraper:")
for method in sorted(scraper_methods):
    print(f"  - {method}")

# Verificar métodos privados críticos (los nuevos)
print("\nMétodos privados críticos:")
critical_methods = [
    '_extraer_nombre_oficial',
    '_extraer_extracto_info',
    '_extraer_bases_reguladoras'
]

for method_name in critical_methods:
    if hasattr(BDNSScraper, method_name):
        print(f"  ✓ {method_name} EXISTE")
        method = getattr(BDNSScraper, method_name)
        # Obtener la firma del método
        sig = inspect.signature(method)
        print(f"    Firma: {sig}")
    else:
        print(f"  ✗ {method_name} NO EXISTE (código desactualizado!)")

# Verificar el método obtener_info_convocatoria
print("\nVerificando obtener_info_convocatoria:")
if hasattr(BDNSScraper, 'obtener_info_convocatoria'):
    print("  ✓ Método existe")
    # Leer el código fuente
    source = inspect.getsource(BDNSScraper.obtener_info_convocatoria)

    # Verificar que llama a los métodos nuevos
    checks = [
        ('nombre_oficial', 'self._extraer_nombre_oficial()'),
        ('extracto_info', 'self._extraer_extracto_info()'),
        ('fecha_publicacion', "extracto_info.get('fecha_publicacion')"),
    ]

    for name, code_snippet in checks:
        if code_snippet in source:
            print(f"  ✓ Extrae '{name}'")
        else:
            print(f"  ✗ NO extrae '{name}' (código desactualizado!)")
else:
    print("  ✗ Método no existe")

print("\n" + "=" * 80)
print("VERIFICACIÓN COMPLETA")
print("=" * 80)
